# Contest Monitor MVP

Телеграм-бот для мониторинга конкурсных списков.

## Что умеет
- `/track <ссылка_на_qs> <unique_code>` — кэширует конкурс при первом обращении, ищет код и подписывает пользователя
- `/myplace` — показывает все отслеживаемые места
- фоновый планировщик обновляет все конкурсы раз в N минут и отправляет уведомления при изменении места

## Установка
1. Создай виртуальное окружение.
2. Установи зависимости:
   ```bash
   pip install -r requirements.txt
   ```
3. Скопируй `.env.example` в `.env` и заполни `BOT_TOKEN`.
4. Инициализируй базу:
   ```bash
   python init_db.py
   ```
5. Запусти бота:
   ```bash
   python main.py
   ```

## Команда track
```bash
/track https://mospolytech.ru/postupayushchim/priem-v-universitet/rating-abiturientov/?qs=... 1234567
```
