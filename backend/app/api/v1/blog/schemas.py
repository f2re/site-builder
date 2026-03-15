# Module: api/v1/blog/schemas.py | Agent: backend-agent | Task: p39_backend_blog_sections
from __future__ import annotations
from pydantic import BaseModel, ConfigDict, Field, EmailStr
from uuid import UUID
from datetime import datetime
from typing import List, Optional, Any
from enum import Enum


class BlogStatus(str, Enum):
    draft = "draft"
    published = "published"
    archived = "archived"


class CommentStatusSchema(str, Enum):
    pending = "pending"
    approved = "approved"
    spam = "spam"


class BlogSection(str, Enum):
    news = "news"
    instructions = "instructions"


class BlogCategoryRead(BaseModel):
    id: UUID
    name: str
    slug: str
    description: Optional[str] = None
    section: Optional[str] = None
    posts_count: int = 0
    model_config = ConfigDict(from_attributes=True)


class BlogCategoryCreate(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None
    section: Optional[str] = None


class BlogCategoryUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None
    section: Optional[str] = None

class TagRead(BaseModel):
    id: UUID
    name: str
    slug: str
    model_config = ConfigDict(from_attributes=True)

class AuthorRead(BaseModel):
    id: UUID
    display_name: str
    name: str = Field(validation_alias="display_name")
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

class AuthorCreate(BaseModel):
    display_name: str
    bio: Optional[str] = None
    avatar_url: Optional[str] = None

class BlogPostBase(BaseModel):
    title: str
    slug: Optional[str] = None
    summary: Optional[str] = None
    content_json: Any = Field(default_factory=lambda: {}, description="TipTap JSON content")
    status: BlogStatus = BlogStatus.draft
    is_featured: bool = False
    category_id: Optional[UUID] = None
    cover_image: Optional[str] = None
    og_image_url: Optional[str] = None
    carousel_images: List[str] = Field(default_factory=list)
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None

class BlogPostUpdate(BaseModel):
    title: Optional[str] = None
    slug: Optional[str] = None
    summary: Optional[str] = None
    content_json: Optional[Any] = None
    content_html: Optional[str] = None  # Frontend might send HTML directly
    status: Optional[BlogStatus] = None
    is_featured: Optional[bool] = None
    category_id: Optional[UUID] = None
    cover_image: Optional[str] = None
    og_image_url: Optional[str] = None
    carousel_images: Optional[List[str]] = None
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    tags: Optional[List[str]] = None

class BlogPostCreate(BlogPostBase):
    category_id: Optional[UUID] = None
    tags: Optional[List[str]] = None

class BlogPostRead(BlogPostBase):
    id: UUID
    content_html: str
    category_id: Optional[UUID]
    author_id: UUID
    published_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    reading_time: int = 0
    reading_time_minutes: int = 0
    views: int = 0
    # Aliases for frontend compatibility
    cover_url: Optional[str] = None
    excerpt: Optional[str] = None

    category: Optional[BlogCategoryRead] = None
    tags: List[TagRead] = []
    author: AuthorRead

    model_config = ConfigDict(from_attributes=True)

class BlogPostShortRead(BaseModel):
    id: UUID
    slug: str
    title: str
    summary: Optional[str] = None
    cover_image: Optional[str] = None
    # Frontend-compatible aliases
    cover_url: Optional[str] = None
    excerpt: Optional[str] = None
    carousel_images: List[str] = []
    category: Optional[BlogCategoryRead] = None
    author: AuthorRead
    tags: List[TagRead] = []
    published_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    reading_time: int = Field(default=0, description="Estimated reading time in minutes")
    reading_time_minutes: int = Field(default=0, description="Alias for reading_time")
    status: BlogStatus

    model_config = ConfigDict(from_attributes=True)

class BlogPagination(BaseModel):
    items: List[BlogPostShortRead]
    next_cursor: Optional[str] = None
    total: int

class CommentBase(BaseModel):
    author_name: str
    body: str

class CommentCreate(CommentBase):
    author_email: EmailStr

class CommentRead(CommentBase):
    id: UUID
    post_id: UUID
    status: CommentStatusSchema
    created_at: datetime
    # We don't include author_email in CommentRead for public API
    model_config = ConfigDict(from_attributes=True)

class CommentAdminRead(CommentRead):
    author_email: str  # This will be decrypted
    model_config = ConfigDict(from_attributes=True)

class BlogPostMediaRead(BaseModel):
    id: UUID
    url: str
    media_type: str
    alt: str
    caption: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    mime_type: str
    size_bytes: int
    sort_order: int = 0
    sequence: int = 1
    base_path: Optional[str] = None
    formats: dict = Field(default_factory=dict)
    model_config = ConfigDict(from_attributes=True)
