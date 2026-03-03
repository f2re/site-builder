"""Blog-related database models."""
import enum
import uuid
from datetime import datetime, timezone
from typing import List, Optional, Any, TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, String, Text, Table, Column, Integer, JSON
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.db.models.user import User


class BlogPostStatus(str, enum.Enum):
    """Blog post publication status."""
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class CommentStatus(str, enum.Enum):
    """Blog post comment status."""
    PENDING = "pending"
    APPROVED = "approved"
    SPAM = "spam"


# Association table for BlogPost <-> Tag
blog_post_tags = Table(
    "blog_post_tags",
    Base.metadata,
    Column("post_id", UUID(as_uuid=True), ForeignKey("blog_posts.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", UUID(as_uuid=True), ForeignKey("blog_tags.id", ondelete="CASCADE"), primary_key=True),
)


class Author(Base):
    """Author profiles linked to User table."""
    __tablename__ = "blog_authors"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    bio: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="blog_author")
    posts: Mapped[List["BlogPost"]] = relationship("BlogPost", back_populates="author")


class BlogCategory(Base):
    """Blog post categories."""
    __tablename__ = "blog_categories"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    posts: Mapped[List["BlogPost"]] = relationship("BlogPost", back_populates="category")


class Tag(Base):
    """Blog post tags."""
    __tablename__ = "blog_tags"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)

    # Relationships
    posts: Mapped[List["BlogPost"]] = relationship(
        "BlogPost", secondary=blog_post_tags, back_populates="tags"
    )


class BlogPost(Base):
    """Blog posts with SEO fields and content."""
    __tablename__ = "blog_posts"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    category_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("blog_categories.id", ondelete="SET NULL"), nullable=True
    )
    author_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("blog_authors.id", ondelete="CASCADE"), nullable=False
    )
    
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Content fields - Task BE-11 refinement
    content_json: Mapped[Any] = mapped_column(JSON().with_variant(JSONB, "postgresql"), nullable=False, server_default='{}')
    content_html: Mapped[str] = mapped_column(Text, nullable=False, server_default='')
    
    status: Mapped[BlogPostStatus] = mapped_column(
        Enum(BlogPostStatus, native_enum=False),
        default=BlogPostStatus.DRAFT,
        nullable=False,
    )
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False)
    cover_image: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    
    # SEO fields
    meta_title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    meta_description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    
    # Metrics
    views: Mapped[int] = mapped_column(Integer, default=0)
    reading_time: Mapped[int] = mapped_column(Integer, default=0)

    # Relationships
    category: Mapped[Optional[BlogCategory]] = relationship("BlogCategory", back_populates="posts")
    author: Mapped[Author] = relationship("Author", back_populates="posts")
    tags: Mapped[List[Tag]] = relationship(
        "Tag", secondary=blog_post_tags, back_populates="posts"
    )
    media: Mapped[List["BlogPostMedia"]] = relationship(
        "BlogPostMedia",
        back_populates="post",
        cascade="all, delete-orphan",
    )
    comments: Mapped[List["Comment"]] = relationship(
        "Comment",
        back_populates="post",
        cascade="all, delete-orphan",
    )


class Comment(Base):
    """Blog post comments."""
    __tablename__ = "blog_comments"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    post_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("blog_posts.id", ondelete="CASCADE"), nullable=False
    )
    author_name: Mapped[str] = mapped_column(String(255), nullable=False)
    author_email: Mapped[str] = mapped_column(Text, nullable=False)  # Fernet encrypted
    body: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[CommentStatus] = mapped_column(
        Enum(CommentStatus, native_enum=False),
        default=CommentStatus.PENDING,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    # Relationships
    post: Mapped[BlogPost] = relationship("BlogPost", back_populates="comments")


class BlogPostMedia(Base):
    """Media files attached to blog posts."""
    __tablename__ = "blog_post_media"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    post_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("blog_posts.id", ondelete="CASCADE"), nullable=True
    )
    
    url: Mapped[str] = mapped_column(String(1000), nullable=False)
    media_type: Mapped[str] = mapped_column(String(10), nullable=False)  # 'image' or 'video'
    alt: Mapped[str] = mapped_column(String(255), nullable=False)
    caption: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    width: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    height: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    mime_type: Mapped[str] = mapped_column(String(50), nullable=False)
    size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    
    # Relationships
    post: Mapped[BlogPost] = relationship("BlogPost", back_populates="media")
