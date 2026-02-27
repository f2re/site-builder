# Module: db/models/blog.py | Agent: backend-agent | Task: phase11_backend_admin_blog_refinement
from __future__ import annotations
import enum
import uuid
from datetime import datetime
from typing import List, Optional, TYPE_CHECKING

from sqlalchemy import String, ForeignKey, Boolean, DateTime, func, Text, Table, Column, Enum, JSON, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from .user import User

# Association table for BlogPost <-> Tag
blog_post_tags = Table(
    "blog_post_tags",
    Base.metadata,
    Column("post_id", ForeignKey("blog_posts.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", ForeignKey("blog_tags.id", ondelete="CASCADE"), primary_key=True),
)

class BlogStatus(str, enum.Enum):
    draft = "draft"
    published = "published"
    archived = "archived"

class BlogCategory(Base):
    __tablename__ = "blog_categories"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)

    posts: Mapped[List[BlogPost]] = relationship("BlogPost", back_populates="category")

class Tag(Base):
    __tablename__ = "blog_tags"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)

    posts: Mapped[List[BlogPost]] = relationship(
        "BlogPost", secondary=blog_post_tags, back_populates="tags"
    )

class BlogPost(Base):
    __tablename__ = "blog_posts"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    category_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("blog_categories.id", ondelete="SET NULL"), nullable=True
    )
    author_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    content_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    content_html: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    summary: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[BlogStatus] = mapped_column(
        Enum(BlogStatus), default=BlogStatus.draft, nullable=False
    )
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False)
    
    cover_image: Mapped[Optional[str]] = mapped_column(String(1000))
    
    views: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    reading_time_minutes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    
    # SEO fields
    meta_title: Mapped[Optional[str]] = mapped_column(String(255))
    meta_description: Mapped[Optional[str]] = mapped_column(String(500))

    category: Mapped[Optional[BlogCategory]] = relationship("BlogCategory", back_populates="posts")
    tags: Mapped[List[Tag]] = relationship(
        "Tag", secondary=blog_post_tags, back_populates="posts"
    )
    author: Mapped[User] = relationship("User")
