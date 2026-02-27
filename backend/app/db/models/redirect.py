from datetime import datetime, timezone
from sqlalchemy import String, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

class Redirect(Base):
    __tablename__ = "redirects"

    id: Mapped[int] = mapped_column(primary_key=True)
    old_path: Mapped[str] = mapped_column(String(500), unique=True, index=True, nullable=False)
    new_path: Mapped[str] = mapped_column(String(500), nullable=False)
    status_code: Mapped[int] = mapped_column(Integer, default=301)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
