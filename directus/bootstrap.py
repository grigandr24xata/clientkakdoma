#!/usr/bin/env python3
"""
Directus bootstrap.
Создаёт все коллекции и связи по schema_v2.md.
Запуск: python directus/bootstrap.py
Idempotent: повторный запуск безопасен.
"""

import os
import time

import requests
from dotenv import load_dotenv

load_dotenv()

DIRECTUS_URL = os.getenv("DIRECTUS_URL", "http://localhost:8055")
ADMIN_EMAIL = os.getenv("DIRECTUS_ADMIN_EMAIL", "admin@example.com")
ADMIN_PASSWORD = os.getenv("DIRECTUS_ADMIN_PASSWORD", "admin123")


def wait_for_directus(timeout=60):
    print("Waiting for Directus...", flush=True)
    for _ in range(timeout):
        try:
            response = requests.get(f"{DIRECTUS_URL}/server/health", timeout=2)
            if response.status_code == 200:
                print("Directus ready.", flush=True)
                return
        except Exception:
            pass
        time.sleep(1)
    raise RuntimeError("Directus did not start")


def get_token() -> str:
    response = requests.post(
        f"{DIRECTUS_URL}/auth/login",
        json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
        timeout=10,
    )
    response.raise_for_status()
    return response.json()["data"]["access_token"]


def h(token):
    return {"Authorization": f"Bearer {token}"}


def field(name, ftype, required=False, default=None, meta_extra=None):
    result = {
        "field": name,
        "type": ftype,
        "meta": {"required": required, **(meta_extra or {})},
        "schema": {},
    }
    if default is not None:
        result["schema"]["default_value"] = default
    return result


def create_collection(token, name, fields):
    payload = {
        "collection": name,
        "meta": {"icon": "box"},
        "schema": {},
        "fields": [
            {
                "field": "id",
                "type": "uuid",
                "meta": {"hidden": True, "readonly": True},
                "schema": {"is_primary_key": True, "has_auto_increment": False},
            }
        ]
        + fields,
    }
    response = requests.post(
        f"{DIRECTUS_URL}/collections", json=payload, headers=h(token), timeout=15
    )
    if response.status_code in (200, 204):
        print(f"  + {name}")
    elif "already exists" in response.text.lower() or response.status_code == 400:
        print(f"  ~ {name} (exists)")
    else:
        print(f"  ! {name}: {response.status_code} {response.text[:120]}")


def create_relation(token, collection, fld, related):
    payload = {
        "collection": collection,
        "field": fld,
        "related_collection": related,
        "meta": {},
        "schema": {"on_delete": "SET NULL"},
    }
    response = requests.post(
        f"{DIRECTUS_URL}/relations", json=payload, headers=h(token), timeout=15
    )
    if response.status_code in (200, 204):
        print(f"  + {collection}.{fld} → {related}")
    else:
        print(f"  ~ {collection}.{fld} → {related} (skip)")


def main():
    wait_for_directus()
    token = get_token()
    print("\n=== Creating collections ===")

    create_collection(
        token,
        "clients",
        [
            field("phone", "string"),
            field("full_name_cyr", "string"),
            field("full_name_latin", "string"),
            field("date_of_birth", "string"),
            field("gender", "string"),
            field("citizenship", "string"),
            field("created_at", "timestamp"),
            field("updated_at", "timestamp"),
        ],
    )

    create_collection(
        token,
        "client_passports",
        [
            field("client_id", "uuid"),
            field("series", "string"),
            field("number", "string"),
            field("issued_by", "string"),
            field("issued_date", "string"),
            field("expiry_date", "string"),
            field("birth_place", "string"),
            field("mrz_raw", "text"),
            field("passport_hash", "string"),
            field("is_current", "boolean", default=True),
            field("ocr_confidence", "float", default=0.0),
            field("auto_accepted", "boolean", default=False),
            field("manual_check", "boolean", default=False),
            field("created_at", "timestamp"),
        ],
    )

    create_collection(
        token,
        "intake_cases",
        [
            field("phone", "string", required=True),
            field("branch", "string"),
            field("resident_count", "integer", default=0),
            field("step", "string"),
            field("status", "string", default="draft"),
            field("created_at", "timestamp"),
            field("updated_at", "timestamp"),
        ],
    )

    create_collection(
        token,
        "intake_residents",
        [
            field("intake_case_id", "uuid"),
            field("order_index", "integer"),
            field("is_main", "boolean", default=False),
            field("ocr_data", "json"),
            field("confirmed", "boolean", default=False),
            field("phone", "string"),
        ],
    )

    create_collection(
        token,
        "owners",
        [
            field("full_name", "string", required=True),
            field("phone", "string"),
            field("payment_day", "integer", default=1),
            field("created_at", "timestamp"),
        ],
    )

    create_collection(
        token,
        "apartments",
        [
            field("address", "string", required=True),
            field("rooms", "integer"),
            field("capacity_residents", "integer"),
            field("monthly_reg_limit", "integer", default=25),
            field("current_reg_count", "integer", default=0),
            field("status", "string", default="free"),
            field("owner_id", "uuid"),
            field("created_at", "timestamp"),
        ],
    )

    create_collection(
        token,
        "deals",
        [
            field("intake_case_id", "uuid"),
            field("main_client_id", "uuid"),
            field("apartment_id", "uuid"),
            field("manager_id", "string"),
            field("branch", "string"),
            field("status", "string", default="draft"),
            field("date_start", "date"),
            field("date_end", "date"),
            field("rent_amount", "float"),
            field("deposit", "float"),
            field("commission", "float"),
            field("registration_fee", "float"),
            field("contract_url", "string"),
            field("act_url", "string"),
            field("video_url", "string"),
            field("payment_confirmed", "boolean", default=False),
            field("created_at", "timestamp"),
            field("updated_at", "timestamp"),
        ],
    )

    create_collection(
        token,
        "deal_residents",
        [
            field("deal_id", "uuid"),
            field("client_id", "uuid"),
            field("is_main", "boolean", default=False),
        ],
    )

    create_collection(
        token,
        "occupancies",
        [
            field("deal_id", "uuid"),
            field("client_id", "uuid"),
            field("apartment_id", "uuid"),
            field("date_start", "date"),
            field("date_end", "date"),
        ],
    )

    create_collection(
        token,
        "registrations",
        [
            field("deal_id", "uuid"),
            field("client_id", "uuid"),
            field("apartment_id", "uuid"),
            field("date_start", "date"),
            field("date_end", "date"),
            field("status", "string", default="planned"),
            field("mfc_doc_url", "string"),
        ],
    )

    create_collection(
        token,
        "payments_client",
        [
            field("deal_id", "uuid"),
            field("type", "string"),
            field("amount", "float"),
            field("currency", "string", default="RUB"),
            field("paid_at", "timestamp"),
            field("confirmed_by", "string"),
            field("payment_method", "string"),
        ],
    )

    create_collection(
        token,
        "payments_owner",
        [
            field("owner_id", "uuid"),
            field("apartment_id", "uuid"),
            field("amount", "float"),
            field("currency", "string", default="RUB"),
            field("planned_date", "date"),
            field("paid_at", "timestamp"),
            field("status", "string", default="planned"),
        ],
    )

    create_collection(
        token,
        "files_media",
        [
            field("entity_type", "string"),
            field("entity_id", "uuid"),
            field("file_type", "string"),
            field("storage_url", "string"),
            field("metadata", "json"),
            field("uploaded_by", "string"),
            field("created_at", "timestamp"),
        ],
    )

    create_collection(
        token,
        "audit_logs",
        [
            field("entity_type", "string"),
            field("entity_id", "uuid"),
            field("action", "string"),
            field("actor_id", "string"),
            field("payload", "json"),
            field("created_at", "timestamp"),
        ],
    )

    print("\n=== Creating relations ===")
    create_relation(token, "client_passports", "client_id", "clients")
    create_relation(token, "intake_residents", "intake_case_id", "intake_cases")
    create_relation(token, "apartments", "owner_id", "owners")
    create_relation(token, "deals", "intake_case_id", "intake_cases")
    create_relation(token, "deals", "main_client_id", "clients")
    create_relation(token, "deals", "apartment_id", "apartments")
    create_relation(token, "deal_residents", "deal_id", "deals")
    create_relation(token, "deal_residents", "client_id", "clients")
    create_relation(token, "occupancies", "deal_id", "deals")
    create_relation(token, "occupancies", "client_id", "clients")
    create_relation(token, "occupancies", "apartment_id", "apartments")
    create_relation(token, "registrations", "deal_id", "deals")
    create_relation(token, "registrations", "client_id", "clients")
    create_relation(token, "registrations", "apartment_id", "apartments")
    create_relation(token, "payments_client", "deal_id", "deals")
    create_relation(token, "payments_owner", "owner_id", "owners")
    create_relation(token, "payments_owner", "apartment_id", "apartments")

    print("\nBootstrap complete.")


if __name__ == "__main__":
    main()
