# Module: db/models/delivery_address.py | Agent: backend-agent | Task: p11_backend_user_addresses
from datetime import datetime, timezone
import uuid
from sqlalchemy import String, Boolean, DateTime, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
import enum


class AddressType(str, enum.Enum):
    HOME = "home"
    PICKUP = "pickup"
    COURIER = "courier"


class DeliveryProvider(str, enum.Enum):
    CDEK = "cdek"
    POCHTA = "pochta"
    OZON = "ozon"
    WB = "wb"
    MANUAL = "manual"


class DeliveryAddress(Base):
    __tablename__ = "delivery_addresses"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # Label (not PII)
    name: Mapped[str] = mapped_column(String(100), nullable=False)

    # PII fields (encrypted)
    recipient_name: Mapped[str] = mapped_column(Text, nullable=False)
    recipient_phone: Mapped[str] = mapped_column(Text, nullable=False)
    recipient_phone_hash: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    full_address: Mapped[str] = mapped_column(Text, nullable=False)

    # Non-PII fields
    address_type: Mapped[AddressType] = mapped_column(
        SQLEnum(AddressType, name="address_type_enum", values_callable=lambda obj: [e.value for e in obj]),
        nullable=False,
    )
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    postal_code: Mapped[str | None] = mapped_column(String(20), nullable=True)
    provider: Mapped[DeliveryProvider] = mapped_column(
        SQLEnum(DeliveryProvider, name="delivery_provider_enum", values_callable=lambda obj: [e.value for e in obj]),
        nullable=False,
    )
    pickup_point_code: Mapped[str | None] = mapped_column(String(100), nullable=True)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    oc_address_id: Mapped[int | None] = mapped_column(nullable=True, index=True, unique=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationship
    user = relationship("User", back_populates="delivery_addresses")
