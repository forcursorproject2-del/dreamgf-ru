from aiogram import Router, F
from aiogram.types import CallbackQuery, PreCheckoutQuery, SuccessfulPayment
from payments.yookassa import YookassaPayment
from db.database import Database
from config.settings import YOOKASSA_SHOP_ID, YOOKASSA_SECRET_KEY
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)
router = Router()

yookassa = YookassaPayment(YOOKASSA_SHOP_ID, YOOKASSA_SECRET_KEY)

@router.callback_query(F.data.startswith("vip_"))
async def process_vip_payment(callback: CallbackQuery, db: Database):
    """Process VIP payment"""
    try:
        data = callback.data.split("_")
        amount = int(data[1])  # 990, 1690, 2990

        # Create payment with discount check
        payment = await yookassa.create_payment(amount, f"VIP DreamGF {amount} руб", callback.from_user.id, session=db.session)

        if payment:
            # Save payment to DB
            await db.create_payment(
                callback.from_user.id,
                payment.id,
                amount,
                "pending"
            )

            # Send invoice
            await callback.bot.send_invoice(
                chat_id=callback.from_user.id,
                title="VIP DreamGF",
                description=f"Получи доступ к безлимит фото и кастом персонажам на {30 if amount == 990 else 90 if amount == 1690 else 365} дней",
                payload=payment.id,
                provider_token="",  # Yookassa doesn't need provider token
                currency="RUB",
                prices=[{"label": f"VIP {amount} руб", "amount": amount * 100}],  # in kopecks
                start_parameter="vip_payment"
            )

            await callback.answer("Счёт создан! Оплати в Telegram.")
        else:
            await callback.answer("Ошибка создания платежа")

    except Exception as e:
        logger.error(f"Payment creation failed: {e}")
        await callback.answer("Ошибка платежа")

@router.pre_checkout_query()
async def process_pre_checkout(pre_checkout: PreCheckoutQuery):
    """Process pre-checkout"""
    await pre_checkout.bot.answer_pre_checkout_query(
        pre_checkout.id,
        ok=True
    )

@router.message(F.successful_payment)
async def process_successful_payment(message: SuccessfulPayment, db: Database):
    """Process successful payment"""
    try:
        payment_id = message.successful_payment.invoice_payload

        # Update payment status
        payment = await db.update_payment_status(payment_id, "completed")

        if payment:
            # Calculate VIP duration
            amount = payment.amount
            if amount == 990:
                days = 30
            elif amount == 1690:
                days = 90
            else:  # 2990
                days = 365

            # Update user VIP status
            vip_until = datetime.now() + timedelta(days=days)
            await db.update_user_vip(payment.user_id, vip_until)

            await message.answer(
                f"💎 Платёж успешен! VIP активирован до {vip_until.strftime('%d.%m.%Y')}\n\n"
                "Теперь у тебя безлимит фото и кастом персонажи! 🎉"
            )

    except Exception as e:
        logger.error(f"Payment processing failed: {e}")
        await message.answer("Ошибка обработки платежа")

def register(dp):
    dp.include_router(router)
