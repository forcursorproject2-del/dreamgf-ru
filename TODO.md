# План деплоя проекта DreamGF в Yandex Cloud

## Шаг 1: Создание Managed PostgreSQL кластера
- Создать кластер PostgreSQL с базой dreamgf
- Получить хост и настроить DATABASE_URL

## Шаг 2: Создание Managed Redis кластера
- Создать кластер Redis
- Получить хост и настроить REDIS_URL

## Шаг 3: Создание Container Registry
- Создать реестр для Docker образов
- Получить ID реестра

## Шаг 4: Сборка и загрузка Docker образа
- Аутентифицироваться в Yandex Container Registry
- Собрать образ из Dockerfile
- Загрузить образ в реестр

## Шаг 5: Создание Serverless Container
- Создать контейнер с образом
- Настроить переменные окружения
- Получить URL контейнера

## Шаг 6: Настройка Telegram Webhook триггера
- Создать триггер для webhook от Telegram
- Установить webhook URL в Telegram боте

## Шаг 7: Тестирование и проверка
- Проверить логи контейнера
- Тестировать работу бота
