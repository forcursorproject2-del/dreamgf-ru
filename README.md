# DreamGF RU 18+ - AI Подруга с Голосом и Фото

Русскоязычная NSFW AI-подруга в Telegram с генерацией фото, голосом, памятью и монетизацией.

## Фичи
- 100% async, aiogram 3.13+
- Бесплатные uncensored модели (DeepSeek, Silero TTS, Flux.1-dev)
- NSFW без цензуры (ролевые игры, секс, мат)
- Память чата 30 дней (Redis)
- Голосовые сообщения (Silero TTS v5_ru)
- Генерация фото 18+ (Flux с LoRA)
- Платежи через ЮKassa
- 12 готовых персонажей
- VIP: безлимит фото + кастом персонаж
- Админка в Telegram
- Авто-сообщения ежедневно
- Защита от бана TG

## Запуск

1. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/your-repo/dreamgf-ru.git
   cd dreamgf-ru
   ```

2. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```

3. Настройте .env:
   ```bash
   cp .env.example .env
   # Заполните переменные
   ```

4. Запустите локально:
   ```bash
   docker-compose up --build
   ```

## Деплой в Yandex Cloud

1. Создайте аккаунт в Yandex Cloud, получите грант.

2. Установите YC CLI:
   ```bash
   curl -sSL https://storage.yandexcloud.net/yandexcloud-yc/install.sh | bash
   yc init
   ```

3. Создайте функцию:
   ```bash
   yc serverless function create --name dreamgf-bot
   yc serverless function version create \
     --function-name dreamgf-bot \
     --runtime python312 \
     --entrypoint main.handler \
     --source-path . \
     --environment BOT_TOKEN=$BOT_TOKEN,OPENROUTER_API_KEY=$OPENROUTER_API_KEY,... \
     --memory 2048mb \
     --execution-timeout 30s
   ```

4. Создайте триггер webhook от Telegram:
   ```bash
   yc serverless trigger create telegram \
     --name telegram-trigger \
     --function-name dreamgf-bot \
     --function-version-id $VERSION_ID \
     --telegram-bot-token $BOT_TOKEN
   ```

5. Для контейнера с Redis/PostgreSQL:
   ```bash
   yc serverless container create --name dreamgf-container --image $IMAGE_URL
   # Аналогично настройте триггеры
   ```

## Структура
- `main.py` - Точка входа
- `bot/` - Логика бота
- `ai/` - ИИ модели
- `db/` - База данных
- `payments/` - Платежи
- `utils/` - Утилиты
- `characters/` - Персонажи

## Команды
- `/start` - Начать
- `/vip` - Купить VIP
- `/newcharacter` - Создать кастом персонажа (VIP)
- Админ: `/stats`, `/broadcast`, `/ban`

## Модели
- DeepSeek-V3 через OpenRouter
- Silero TTS v5_ru
- Flux.1-dev с LoRA из Civitai

## Безопасность
- NSFW только в приват чате
- Watermark на фото для бесплатных
- Rate limit 30 сообщ/мин
