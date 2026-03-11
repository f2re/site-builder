# Module: db/models/migration.py | Agent: orchestrator | Task: opencart_migration
import enum
import uuid
from datetime import datetime, timezone
from sqlalchemy import Integer, DateTime, JSON, Enum as SAEnum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

class MigrationStatus(str, enum.Enum):
    PENDING  = "pending"
    RUNNING  = "running"
    PAUSED   = "paused"
    DONE     = "done"
    FAILED   = "failed"

class MigrationEntity(str, enum.Enum):
    USERS      = "users"
    CATEGORIES = "categories"
    PRODUCTS   = "products"
    IMAGES     = "images"
    ORDERS     = "orders"
    BLOG       = "blog"
    DEVICES    = "devices"
    ADDRESSES  = "addresses"

class MigrationJob(Base):
    __tablename__ = "migration_jobs"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    entity: Mapped[MigrationEntity] = mapped_column(SAEnum(MigrationEntity), nullable=False)
    status: Mapped[MigrationStatus] = mapped_column(SAEnum(MigrationStatus), default=MigrationStatus.PENDING)
    
    total: Mapped[int] = mapped_column(Integer, default=0)
    processed: Mapped[int] = mapped_column(Integer, default=0)
    skipped: Mapped[int] = mapped_column(Integer, default=0)
    failed: Mapped[int] = mapped_column(Integer, default=0)
    
    last_oc_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    errors: Mapped[list | None] = mapped_column(JSON, nullable=True)
    extra_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

class MigrationLog(Base):
    __tablename__ = "migration_logs"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    job_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("migration_jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    level: Mapped[str] = mapped_column(String(10), default="INFO")   # INFO / WARN / ERROR
    message: Mapped[str] = mapped_column(Text, nullable=False)
    oc_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
