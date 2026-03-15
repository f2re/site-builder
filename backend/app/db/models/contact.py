# Module: db/models/contact.py | Agent: backend-agent | Task: p43_backend_feedback
"""
Models for contact form (ContactMessage) and site settings (SiteSettings).
PII fields (name, email, phone) are encrypted at rest via Fernet (152-FZ).
"""
import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum, String, Text, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ContactStatus(str, enum.Enum):
    NEW = "NEW"
    READ = "READ"
    REPLIED = "REPLIED"


class ContactMessage(Base):
    __tablename__ = "contact_message"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)

    # PII fields — encrypted at rest via Fernet (152-FZ)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    email: Mapped[str] = mapped_column(Text, nullable=False)
    phone: Mapped[str | None] = mapped_column(Text, nullable=True)

    subject: Mapped[str] = mapped_column(String(500), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)

    status: Mapped[ContactStatus] = mapped_column(
        Enum(ContactStatus, name="contactstatus"),
        default=ContactStatus.NEW,
        nullable=False,
    )

    # IP address is NOT personal data per 152-FZ without other identifying info
    ip_address: Mapped[str] = mapped_column(String(45), nullable=False, default="")

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    read_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )


class SiteSettings(Base):
    __tablename__ = "site_settings"

    __table_args__ = (UniqueConstraint("key", name="uq_site_settings_key"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    key: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    value: Mapped[str | None] = mapped_column(Text, nullable=True)
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=True,
    )
