import asyncio
from pathlib import Path
from typing import Dict, Any
from app.tasks.celery_app import celery_app
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from app.core.config import settings
from aiogram import Bot
from app.core.logging import logger

# Using dynamic path relative to this file to avoid errors during tests
BASE_PATH = Path(__file__).resolve().parents[2]
TEMPLATE_FOLDER = BASE_PATH / "templates" / "email"

mail_conf = ConnectionConfig(
    MAIL_USERNAME=settings.SMTP_USER,
    MAIL_PASSWORD=settings.SMTP_PASSWORD,
    MAIL_FROM=settings.EMAILS_FROM_EMAIL,
    MAIL_PORT=settings.SMTP_PORT,
    MAIL_SERVER=settings.SMTP_HOST,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    TEMPLATE_FOLDER=TEMPLATE_FOLDER
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

    async def _send():
        await fm.send_message(message, template_name=template_name)

    try:
        asyncio.run(_send())
    except Exception as e:
        logger.error("email_send_failed", recipient=recipient, error=str(e))
        raise

@celery_app.task(name="tasks.send_telegram")
def send_telegram_task(chat_id: str, message: str):
    """Celery task to send telegram messages using aiogram."""
    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)

    async def _send():
        async with bot:
            await bot.send_message(chat_id=chat_id, text=message, parse_mode="HTML")

    try:
        asyncio.run(_send())
    except Exception as e:
        logger.error("telegram_send_failed", chat_id=chat_id, error=str(e))
        raise

@celery_app.task(name="tasks.send_sms_stub")
def send_sms_stub_task(phone: str, message: str):
    """SMS Stub - just log it."""
    logger.info("sms_sent_stub", phone=phone, message=message)


@celery_app.task(name="tasks.send_contact_notification")
def send_contact_notification_task(
    recipient: str,
    sender_name: str,
    sender_email: str,
    subject: str,
    message: str,
) -> None:
    """Send an email notification to the site admin about a new contact form submission."""
    fm = FastMail(mail_conf)
    body = (
        f"<p>Новая заявка обратной связи</p>"
        f"<p><b>Имя:</b> {sender_name}</p>"
        f"<p><b>Email:</b> {sender_email}</p>"
        f"<p><b>Тема:</b> {subject}</p>"
        f"<p><b>Сообщение:</b></p>"
        f"<p>{message}</p>"
    )
    message_schema = MessageSchema(
        subject=f"Новая заявка: {subject}",
        recipients=[recipient],
        body=body,
        subtype=MessageType.html,
    )

    async def _send():
        await fm.send_message(message_schema)

    try:
        asyncio.run(_send())
    except Exception as exc:
        logger.error(
            "contact_notification_send_failed",
            recipient=recipient,
            error=str(exc),
        )
        raise
