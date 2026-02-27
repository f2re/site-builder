# Module: db/models/user.py | Agent: backend-agent | Task: phase7_backend_security
from datetime import datetime, timezone
import uuid
from sqlalchemy import String, Boolean, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    
    # Blind index for searching. SHA256 length is 64.
    email_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    
    # Encrypted data (PII)
    # Fernet ciphertext for 255 chars can be around 380 chars. Text or String(1024) is safer.
    email: Mapped[str] = mapped_column(Text, nullable=False)
    full_name: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
    # Role: 'customer' | 'manager' | 'admin'
    role: Mapped[str] = mapped_column(String(50), default="customer")
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
    blog_posts = relationship("BlogPost", back_populates="author", lazy="selectin")
