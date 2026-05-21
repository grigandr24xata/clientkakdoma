# Telegram Adapter

Тонкий Telegram adapter поверх backend API.

## Архитектура
- Не хранит workflow state — всё в backend
- BackendClient проксирует вызовы в backend API
- FSM state только для текущего шага диалога

## Запуск
```bash
# Убедись что backend запущен:
uvicorn backend.main:app --port 8000

# Запустить adapter:
python -m adapters.telegram.main
```

## Flow
1. /start → ввод телефона → SMS код → JWT
2. Выбор ветки (A: квартира+регистрация / B: только регистрация)
3. Количество жильцов
4. Паспорт каждого жильца → OCR → подтверждение
5. Доп.документы (опционально)
6. Финальное подтверждение → submit

## Legacy
bot/ — старый runtime, только reference. Не использовать.
