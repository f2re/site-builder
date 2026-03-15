# Module: db/models/user_device.py | Agent: backend-agent | Task: p36_backend_device_models
import uuid
import enum
from datetime import datetime, timezone
from typing import TYPE_CHECKING, List

from sqlalchemy import String, Boolean, DateTime, ForeignKey, Integer, Text, Enum, Table, Column, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

if TYPE_CHECKING:
    from app.db.models.firmware import ModuleComplectation


class DeviceModel(str, enum.Enum):
    WIFI_OBD2 = "wifi_obd2"
    WIFI_OBD2_ADVANCED = "wifi_obd2_advanced"


# Association table: UserDevice <-> ModuleComplectation
user_device_complectations = Table(
    "user_device_complectations",
    Base.metadata,
    Column("user_device_id", Uuid, ForeignKey("user_devices.id", ondelete="CASCADE"), primary_key=True),
    Column("complectation_id", Uuid, ForeignKey("module_complectations.id", ondelete="CASCADE"), primary_key=True),
)


class UserDevice(Base):
    """OBD2 / IoT device owned by a user."""

    __tablename__ = "user_devices"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    # Hardware identifier — MAC address, serial number, etc.
    device_uid: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    model: Mapped[DeviceModel] = mapped_column(
        Enum(DeviceModel, values_callable=lambda x: [e.value for e in x], native_enum=False),
        nullable=False,
        default=DeviceModel.WIFI_OBD2,
    )
    firmware_version: Mapped[str | None] = mapped_column(String(50), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_seen_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    registered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    # OpenCart migration fields
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    oc_device_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True, unique=True)
    module_device_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("module_devices.id", ondelete="SET NULL"), nullable=True, index=True
    )

    # Relationships
    user = relationship("User", back_populates="devices", lazy="selectin")
    module_device = relationship("ModuleDevice", foreign_keys=[module_device_id])
    complectations: Mapped[List["ModuleComplectation"]] = relationship(
        "ModuleComplectation", secondary=user_device_complectations, lazy="selectin"
    )
