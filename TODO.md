# Адаптация под Render Free

## Выполнено
- [x] Анализ кода и планирование

## В работе
- [ ] utils/cache.py — заменить Redis на memory cache с fallback
- [ ] ai/image_gen.py — генерация фото через OpenRouter API
- [ ] docker-compose.yml — убрать Redis и Postgres
- [ ] Dockerfile — обновить для минимального образа
- [ ] Тестирование изменений

## Детали
1. **utils/cache.py**: Удалить `import redis.asyncio`, заменить на dict + asyncio.Lock с TTL
2. **ai/image_gen.py**: httpx.AsyncClient, model: black-forest-labs/flux-dev, prompt с Russian girl, сохранить в temp/
3. **docker-compose.yml**: Только сервис bot, volumes для data, temp, characters, lora
4. **Dockerfile**: FROM python:3.12-slim, без torch/diffusers
