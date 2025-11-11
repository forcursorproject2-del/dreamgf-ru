import asyncio
import logging
from bot.init import dp, bot
from bot.loader import on_startup, on_shutdown, register_handlers
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
import os

# Configure logging
logging.basicConfig(level=logging.INFO)

async def main():
    """Main function"""
    # Register handlers
    register_handlers()

    # Webhook mode for production
    if os.getenv("WEBHOOK_URL"):
        webhook_url = os.getenv("WEBHOOK_URL")
        webhook_path = "/webhook"

        # Set webhook
        await bot.set_webhook(
            url=f"{webhook_url}{webhook_path}",
            drop_pending_updates=True
        )

        # Create aiohttp app
        app = web.Application()

        # Create webhook handler
        webhook_handler = SimpleRequestHandler(
            dispatcher=dp,
            bot=bot,
            webhook_path=webhook_path
        )

        # Register webhook handler
        webhook_handler.register(app, path=webhook_path)

        # Add startup/shutdown handlers
        app.on_startup.append(on_startup)
        app.on_shutdown.append(on_shutdown)

        # Run server
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, host="0.0.0.0", port=int(os.getenv("PORT", 8080)))
        await site.start()

        logging.info(f"Webhook server started on port {os.getenv('PORT', 8080)}")

        # Keep running
        try:
            await asyncio.Future()  # Run forever
        except KeyboardInterrupt:
            logging.info("Shutting down...")
        finally:
            await runner.cleanup()
            await bot.session.close()

    else:
        # Polling mode for development
        await on_startup()
        try:
            await dp.start_polling(bot)
        finally:
            await on_shutdown()

if __name__ == "__main__":
    asyncio.run(main())
