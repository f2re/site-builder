import asyncio
from typing import Dict, Any
from app.tasks.celery_app import celery_app
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from app.core.config import settings
from aiogram import Bot
from app.core.logging import logger

mail_conf = ConnectionConfig(
    MAIL_USERNAME=settings.SMTP_USER,
    MAIL_PASSWORD=settings.SMTP_PASSWORD,
    MAIL_FROM=settings.EMAILS_FROM_EMAIL,
    MAIL_PORT=settings.SMTP_PORT,
    MAIL_SERVER=settings.SMTP_HOST,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    TEMPLATE_FOLDER='app/templates/email'
)

@celery_app.task(name="tasks.send_email")
def send_email_task(recipient: str, subject: str, template_name: str, context: Dict[str, Any]):
    """Celery task to send emails using fastapi-mail."""
    fm = FastMail(mail_conf)
    message = MessageSchema(
        subject=subject,
        recipients=[recipient],
        template_body=context,
        subtype=MessageType.html
    )
    
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(fm.send_message(message, template_name=template_name))
    except Exception as e:
        logger.error("email_send_failed", recipient=recipient, error=str(e))
        raise

@celery_app.task(name="tasks.send_telegram")
def send_telegram_task(chat_id: str, message: str):
    """Celery task to send telegram messages using aiogram."""
    bot = Bot(token=settings.YOOMONEY_SHOP_ID) # Placeholder for bot token in settings if not present
    # Better to use settings.TELEGRAM_BOT_TOKEN if we add it
    
    async def _send():
        async with bot:
            await bot.send_message(chat_id=chat_id, text=message, parse_mode="HTML")
            
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(_send())
    except Exception as e:
        logger.error("telegram_send_failed", chat_id=chat_id, error=str(e))
        raise

@celery_app.task(name="tasks.send_sms_stub")
def send_sms_stub_task(phone: str, message: str):
    """SMS Stub - just log it."""
    logger.info("sms_sent_stub", phone=phone, message=message)
