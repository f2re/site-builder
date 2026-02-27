"""Blog-related database models."""
from datetime import datetime
from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.db.base import Base


class BlogPostStatus(str, enum.Enum):
    """Blog post publication status."""
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class BlogCategory(Base):
    """Blog post categories."""
    __tablename__ = "blog_category"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    posts: Mapped[list["BlogPost"]] = relationship("BlogPost", back_populates="category")


class BlogPost(Base):
    """Blog posts with SEO fields and content in JSON + HTML."""
    __tablename__ = "blog_post"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(200), unique=True, index=True, nullable=False)
    excerpt: Mapped[str] = mapped_column(String(300), nullable=False)
    
    # Content in two formats
    content_json: Mapped[dict] = mapped_column(JSONB, nullable=False)  # TipTap JSON
    content_html: Mapped[str] = mapped_column(Text, nullable=False)  # Sanitized HTML
    
    # SEO fields
    meta_title: Mapped[str | None] = mapped_column(String(60), nullable=True)
    meta_description: Mapped[str | None] = mapped_column(String(160), nullable=True)
    og_image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    
    # Relationships
    category_id: Mapped[int | None] = mapped_column(ForeignKey("blog_category.id"), nullable=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    
    # Status and dates
    status: Mapped[str] = mapped_column(
        Enum(BlogPostStatus, native_enum=False),
        default=BlogPostStatus.DRAFT,
        nullable=False,
    )
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )
    
    # Metrics
    views: Mapped[int] = mapped_column(Integer, default=0)
    reading_time_minutes: Mapped[int] = mapped_column(Integer, default=0)
    
    # Relationships
    category: Mapped[BlogCategory | None] = relationship("BlogCategory", back_populates="posts")
    author: Mapped["User"] = relationship("User", back_populates="blog_posts")
    media: Mapped[list["BlogPostMedia"]] = relationship(
        "BlogPostMedia",
        back_populates="post",
        cascade="all, delete-orphan",
    )


class BlogPostMedia(Base):
    """Media files (images/videos) attached to blog posts."""
    __tablename__ = "blog_post_media"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    post_id: Mapped[int | None] = mapped_column(ForeignKey("blog_post.id"), nullable=True)
    
    url: Mapped[str] = mapped_column(String(500), nullable=False)  # MinIO path
    media_type: Mapped[str] = mapped_column(String(10), nullable=False)  # 'image' or 'video'
    alt: Mapped[str] = mapped_column(String(200), nullable=False)  # Required for SEO
    caption: Mapped[str | None] = mapped_column(String(500), nullable=True)
    
    # Dimensions (for images only)
    width: Mapped[int | None] = mapped_column(Integer, nullable=True)
    height: Mapped[int | None] = mapped_column(Integer, nullable=True)
    
    mime_type: Mapped[str] = mapped_column(String(50), nullable=False)
    size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    
    # Relationships
    post: Mapped["BlogPost"] = relationship("BlogPost", back_populates="media")
