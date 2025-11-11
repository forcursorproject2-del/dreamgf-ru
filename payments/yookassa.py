import yookassa
from yookassa import Payment
from config.settings import YOOKASSA_SHOP_ID, YOOKASSA_SECRET_KEY
from sqlalchemy import func
from db.models import Payment as DBPayment
from sqlalchemy.ext.asyncio import AsyncSession
import logging

logger = logging.getLogger(__name__)

class YookassaPayment:
    def __init__(self):
        yookassa.Configuration.configure(YOOKASSA_SHOP_ID, YOOKASSA_SECRET_KEY)

    async def create_payment(self, amount: int, description: str, user_id: int, return_url: str = "https://t.me/dreamgf_ru_bot", session: AsyncSession = None):
        """Create payment via Yookassa"""
        try:
            # Check for discount for first 100 payments
            total_payments = await session.execute(func.count(DBPayment.id))
            if total_payments.scalar() < 100 and amount == 990:
                amount = 495  # 50% discount

            payment = Payment.create({
                "amount": {
                    "value": f"{amount}.00",
                    "currency": "RUB"
                },
                "confirmation": {
                    "type": "redirect",
                    "return_url": return_url
                },
                "capture": True,
                "description": description,
                "metadata": {
                    "user_id": str(user_id)
                }
            })
            return {
                "id": payment.id,
                "url": payment.confirmation.confirmation_url,
                "status": payment.status
            }
        except Exception as e:
            logger.error(f"Payment creation failed: {e}")
            return None

    async def check_payment_status(self, payment_id: str):
        """Check payment status"""
        try:
            payment = Payment.find_one(payment_id)
            return payment.status
        except Exception as e:
            logger.error(f"Payment status check failed: {e}")
            return None

    async def get_payment_info(self, payment_id: str):
        """Get full payment info"""
        try:
            return Payment.find_one(payment_id)
        except Exception as e:
            logger.error(f"Payment info retrieval failed: {e}")
            return None
