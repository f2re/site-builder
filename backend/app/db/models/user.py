# Module: db/models/user.py | Agent: backend-agent | Task: Phase 1 Dashfirm
from datetime import datetime, timezone
import uuid
from typing import TYPE_CHECKING
from sqlalchemy import String, Boolean, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

if TYPE_CHECKING:
    from app.db.models.firmware import ModuleToken


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    
    # Blind index for searching. SHA256 length is 64.
    email_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)

    # Encrypted data (PII)
    # Fernet ciphertext for 255 chars can be around 380 chars. Text or String(1024) is safer.
    email: Mapped[str] = mapped_column(Text, nullable=False)
    email_normalized: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    full_name: Mapped[str | None] = mapped_column(Text, nullable=True)
    full_name_normalized: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    phone: Mapped[str | None] = mapped_column(Text, nullable=True)
    phone_hash: Mapped[str | None] = mapped_column(String(64), index=True, nullable=True)
    phone_normalized: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    hashed_password: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
    # Role: 'customer' | 'manager' | 'admin'
    role: Mapped[str] = mapped_column(String(50), default="customer")
    
    # OAuth
    auth_provider: Mapped[str] = mapped_column(String(50), default="local")
    provider_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_login_ip: Mapped[str | None] = mapped_column(String(50), nullable=True)
    last_login_device: Mapped[str | None] = mapped_column(String(255), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    orders = relationship("Order", back_populates="user", lazy="selectin")
    devices = relationship("UserDevice", back_populates="user", lazy="selectin")
    delivery_addresses = relationship("DeliveryAddress", back_populates="user", lazy="selectin")

    # Blog relationships
    blog_author = relationship("Author", back_populates="user", uselist=False, lazy="selectin")

    # Firmware Management
    module_token: Mapped["ModuleToken"] = relationship("ModuleToken", back_populates="user", uselist=False)