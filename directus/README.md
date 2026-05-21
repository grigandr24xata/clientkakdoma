# Directus

CRM backoffice для менеджеров и руководителя.

Сущности: clients, passports, intake_cases, apartments, owners, deals, deal_residents, occupancies, registrations, payments_client, payments_owner, files_media, audit_logs.

## Запуск bootstrap

```bash
# 1. Поднять postgres и directus:
docker compose -f infra/docker-compose.dev.yml up -d postgres directus

# 2. Дождаться ~30 сек пока Directus стартует, затем:
python directus/bootstrap.py

# Скрипт создаст все 14 коллекций и связи.
# Idempotent — повторный запуск безопасен.

# 3. Открыть Directus:
# http://localhost:8055
# admin@example.com / admin123
```
