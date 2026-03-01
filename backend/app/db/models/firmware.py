# Module: db/models/firmware.py | Agent: backend-agent | Task: Phase 1 Dashfirm
from datetime import datetime, timezone
import uuid
from typing import TYPE_CHECKING, List
from sqlalchemy import String, Boolean, DateTime, Text, ForeignKey, Integer, Enum, Table, Column, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
import enum

if TYPE_CHECKING:
    from app.db.models.user import User

class DeviceType(str, enum.Enum):
    OBD = "OBD"
    AFR = "AFR"

# Association Table: DeviceComplectation
device_complectations = Table(
    "device_complectations",
    Base.metadata,
    Column("device_serial", String(255), ForeignKey("module_devices.serial", ondelete="CASCADE"), primary_key=True),
    Column("complectation_id", Uuid, ForeignKey("module_complectations.id", ondelete="CASCADE"), primary_key=True),
)

class ModuleToken(Base):
    __tablename__ = "module_tokens"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    token: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="module_token")
    devices: Mapped[List["ModuleDevice"]] = relationship("ModuleDevice", back_populates="token", cascade="all, delete-orphan")

class ModuleDevice(Base):
    __tablename__ = "module_devices"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    token_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("module_tokens.id", ondelete="CASCADE"), nullable=False)
    serial: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    device_type: Mapped[DeviceType] = mapped_column(Enum(DeviceType, name="device_type_enum"), nullable=False)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    token: Mapped["ModuleToken"] = relationship("ModuleToken", back_populates="devices")
    complectations: Mapped[List["ModuleComplectation"]] = relationship(
        "ModuleComplectation", secondary=device_complectations, back_populates="devices"
    )

class ModuleComplectation(Base):
    __tablename__ = "module_complectations"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    caption: Mapped[str] = mapped_column(String(255), nullable=False)
    label: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    code: Mapped[int] = mapped_column(Integer, nullable=False)
    simple: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships
    devices: Mapped[List["ModuleDevice"]] = relationship(
        "ModuleDevice", secondary=device_complectations, back_populates="complectations"
    )
