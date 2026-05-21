from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
import uuid


@dataclass
class OCRRunMetric:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    intake_resident_id: str | None = None
    correlation_id: str = ""
    primary_engine: str = "paddle"
    primary_confidence: float = 0.0
    checksums_passed: bool = False
    cross_validation_passed: bool = False
    auto_accepted: bool = False
    fallback_stage_reached: str | None = None
    final_source: str = "paddle"
    manual_check: bool = False
    manual_review_outcome: str | None = None
    sla_breach: bool = False
    warnings: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))


_metrics_store: list[OCRRunMetric] = []


def record_ocr_metric(
    *,
    correlation_id: str,
    ocr_result: dict[str, Any],
    intake_resident_id: str | None = None,
) -> OCRRunMetric:
    """Записать метрику после OCR run. Вызывать из backend/ocr/service.py."""
    parsing_source = ocr_result.get("parsing_source", "paddle")
    fallback_stage = parsing_source if parsing_source != "paddle" else None
    warnings = ocr_result.get("warnings", [])

    metric = OCRRunMetric(
        intake_resident_id=intake_resident_id,
        correlation_id=correlation_id,
        primary_engine="paddle",
        primary_confidence=float(ocr_result.get("confidence_score") or 0.0),
        checksums_passed="checksum_failed" not in warnings,
        cross_validation_passed="cross_validation_failed" not in warnings,
        auto_accepted=bool(ocr_result.get("auto_accepted")),
        fallback_stage_reached=fallback_stage,
        final_source=parsing_source,
        manual_check=bool(ocr_result.get("manual_check")),
        sla_breach=bool(ocr_result.get("sla_breach")),
        warnings=warnings,
    )
    _metrics_store.append(metric)
    return metric


def get_metrics_summary() -> dict[str, Any]:
    """Агрегированная сводка для OCR quality dashboard."""
    total = len(_metrics_store)
    if total == 0:
        return {"total": 0}

    auto_accepted = sum(1 for m in _metrics_store if m.auto_accepted)
    manual_check = sum(1 for m in _metrics_store if m.manual_check)
    fallback_used = sum(1 for m in _metrics_store if m.fallback_stage_reached is not None)
    by_source: dict[str, int] = {}
    for m in _metrics_store:
        by_source[m.final_source] = by_source.get(m.final_source, 0) + 1

    return {
        "total": total,
        "auto_accepted_rate": round(auto_accepted / total, 3),
        "manual_check_rate": round(manual_check / total, 3),
        "fallback_rate": round(fallback_used / total, 3),
        "by_final_source": by_source,
    }


def get_ocr_quality_dashboard() -> dict[str, Any]:
    total = len(_metrics_store)
    if total == 0:
        return {"total": 0, "message": "No OCR runs recorded yet"}

    auto_accepted = [m for m in _metrics_store if m.auto_accepted]
    manual_check = [m for m in _metrics_store if m.manual_check]
    fallback_used = [m for m in _metrics_store if m.fallback_stage_reached is not None]
    sla_breach = [m for m in _metrics_store if m.sla_breach]

    by_source: dict[str, int] = {}
    for m in _metrics_store:
        by_source[m.final_source] = by_source.get(m.final_source, 0) + 1

    avg_confidence = sum(m.primary_confidence for m in _metrics_store) / total

    problematic = [m for m in _metrics_store if m.manual_check or m.sla_breach]
    recent_problematic = sorted(problematic, key=lambda m: m.created_at, reverse=True)[:10]

    from datetime import date, timedelta

    today = date.today()
    daily_trend: dict[str, dict[str, float | int]] = {}
    for i in range(7):
        day = today - timedelta(days=i)
        day_str = day.isoformat()
        day_runs = [m for m in _metrics_store if m.created_at.date() == day]
        if day_runs:
            day_auto = sum(1 for m in day_runs if m.auto_accepted)
            daily_trend[day_str] = {
                "total": len(day_runs),
                "auto_accepted": day_auto,
                "auto_accepted_rate": round(day_auto / len(day_runs), 3),
            }

    return {
        "total": total,
        "rates": {
            "auto_accepted": round(len(auto_accepted) / total, 3),
            "manual_check": round(len(manual_check) / total, 3),
            "fallback_used": round(len(fallback_used) / total, 3),
            "sla_breach": round(len(sla_breach) / total, 3),
        },
        "avg_confidence": round(avg_confidence, 3),
        "by_final_source": by_source,
        "recent_problematic": [
            {
                "id": m.id,
                "correlation_id": m.correlation_id,
                "intake_resident_id": m.intake_resident_id,
                "final_source": m.final_source,
                "confidence": m.primary_confidence,
                "manual_check": m.manual_check,
                "sla_breach": m.sla_breach,
                "warnings": m.warnings,
                "created_at": m.created_at.isoformat(),
            }
            for m in recent_problematic
        ],
        "daily_trend": daily_trend,
    }


def get_low_confidence_runs(threshold: float = 0.6) -> list[dict[str, Any]]:
    """Запуски с низкой уверенностью — кандидаты на ручную проверку."""
    return [
        {
            "id": m.id,
            "correlation_id": m.correlation_id,
            "intake_resident_id": m.intake_resident_id,
            "confidence": m.primary_confidence,
            "final_source": m.final_source,
            "warnings": m.warnings,
            "created_at": m.created_at.isoformat(),
        }
        for m in _metrics_store
        if m.primary_confidence < threshold and not m.auto_accepted
    ]
