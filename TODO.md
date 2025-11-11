# TODO: Добавить систему фри-триала в DreamGF RU бот

## Задачи:
- [x] Изменить модель User в db/models.py: добавить поля trial_messages, trial_photo_used, trial_voice_used, trial_ended
- [x] Создать middleware bot/middlewares/trial.py
- [x] Подключить middleware в bot/loader.py
- [x] Изменить bot/handlers/message.py: добавить проверку trial_allowed
- [x] Изменить ai/image_gen.py: добавить водяной знак только если НЕ VIP и триал кончился
- [x] Изменить ai/voice_tts.py: добавить водяной знак только если НЕ VIP и триал кончился (если применимо)
- [x] Изменить payments/yookassa.py: добавить скидку первым 100 платежам

## Followup:
- [ ] Протестировать миграцию базы данных
- [ ] Проверить работу middleware
- [ ] Проверить лимиты и блокировки
