# Contest Monitor MVP

Телеграм-бот для мониторинга конкурсных списков.

## Что умеет
- `/code` — сохраняет уникальный код абитуриента
- `/track <ссылка_на_qs>` — кэширует конкурс при первом обращении, ищет код и подписывает пользователя
- `/myplace` — показывает все отслеживаемые места
- фоновый планировщик обновляет все конкурсы раз в N минут и отправляет уведомления при изменении места

## Порядок установки

1. Создать пустую папку для проекта (можно в любой директории) и склонировать репозиторий:
   ```bash
   mkdir "ProjectFolder"
   cd ProjectFolder
   git clone github.com/kingoil01/an-intelligent-assistant-for-mospolytech-applicants
   ```
   Перейти в созданную после git clone папку.
2. Создать виртуальное окружение.
3. Установить зависимости:
   ```bash
   pip install -r requirements.txt
   ```
4. Скопировать `.env.example` в `.env` и заполнить параметры.
5. Запустить бота:
   ```bash
   python main.py
   ```

## Команда track
```bash
/track https://mospolytech.ru/postupayushchim/priem-v-universitet/rating-abiturientov/?qs=...
```
