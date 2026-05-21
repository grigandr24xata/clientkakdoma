from backend.audit.service import log_action
from backend.deals.models import Deal


def create_deal_from_intake(intake_case) -> Deal:
    """Создать сделку после submit intake. Вызывается из intake submit endpoint."""
    from backend.deals.models import Deal, DealBranch, DealResident, DealStatus
    from backend.deals.store import create_deal
    from backend.clients.store import find_by_passport, create_client
    from backend.clients.models import ClientPassport

    residents = []
    main_client_id = None

    for resident in intake_case.residents:
        if not resident.ocr_data:
            continue
        fields = resident.ocr_data.get("fields", {})

        series = fields.get("series", "")
        number = fields.get("passport_number", "")
        existing = find_by_passport(series, number) if series and number else None

        if existing:
            client_id = existing.id
        else:
            new_client = create_client(
                {
                    "phone": resident.phone or "",
                    "full_name_cyr": fields.get("full_name_cyr", ""),
                    "full_name_latin": fields.get("given_names", "") + " " + fields.get("surname", ""),
                    "date_of_birth": fields.get("date_of_birth", ""),
                    "citizenship": fields.get("nationality", ""),
                    "passports": [
                        ClientPassport(
                            series=series,
                            number=number,
                            mrz_raw=resident.ocr_data.get("mrz_raw", ""),
                            passport_hash=fields.get("passport_hash", ""),
                            ocr_confidence=resident.ocr_data.get("confidence_score", 0.0),
                            auto_accepted=resident.ocr_data.get("auto_accepted", False),
                            manual_check=resident.ocr_data.get("manual_check", False),
                        ).model_dump()
                    ],
                }
            )
            client_id = new_client.id

        if resident.is_main:
            main_client_id = client_id

        residents.append(DealResident(client_id=client_id, is_main=resident.is_main))

    deal = Deal(
        intake_case_id=intake_case.id,
        main_client_id=main_client_id or "",
        branch=DealBranch(intake_case.branch.value),
        status=DealStatus.client_data_collected,
        residents=residents,
    )
    created = create_deal(deal)
    log_action(entity_type="deal", entity_id=created.id, action="deal_created", actor_id="system")
    return created


def check_activation_conditions(deal: Deal) -> bool:
    """Проверить все условия для перехода в active."""
    return all(
        [
            deal.apartment_id is not None,
            deal.contract_url is not None,
            deal.act_url is not None,
            deal.video_url is not None,
            deal.payment_confirmed is True,
        ]
    )


def try_activate_deal(deal: Deal) -> Deal:
    """Если все условия выполнены — перевести в active."""
    from backend.deals.models import DealStatus
    from backend.deals.store import update_deal

    if check_activation_conditions(deal):
        deal.status = DealStatus.active
        updated = update_deal(deal)
        log_action(entity_type="deal", entity_id=updated.id, action="deal_activated", actor_id="system")
        return updated
    return deal
