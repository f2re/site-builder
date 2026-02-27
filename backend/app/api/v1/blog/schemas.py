# Module: api/v1/blog/schemas.py | Agent: backend-agent | Task: BE-02
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

class BlogCategoryRead(BaseModel):
    id: UUID
    name: str
    slug: str
    description: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class TagRead(BaseModel):
    id: UUID
    name: str
    slug: str
    model_config = ConfigDict(from_attributes=True)

class AuthorRead(BaseModel):
    id: UUID
    display_name: str
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class AuthorCreate(BaseModel):
    display_name: str
    bio: Optional[str] = None
    avatar_url: Optional[str] = None

class BlogPostBase(BaseModel):
    title: str
    slug: Optional[str] = None
    summary: Optional[str] = None
    content_json: Any = Field(default_factory=dict, description="TipTap JSON content")
    status: BlogStatus = BlogStatus.draft
    is_featured: bool = False
    category_id: Optional[UUID] = None
    cover_image: Optional[str] = None
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None

class BlogPostUpdate(BaseModel):
    title: Optional[str] = None
    slug: Optional[str] = None
    summary: Optional[str] = None
    content_json: Optional[Any] = None
    status: Optional[BlogStatus] = None
    is_featured: Optional[bool] = None
    category_id: Optional[UUID] = None
    cover_image: Optional[str] = None
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None

class BlogPostCreate(BlogPostBase):
    category_id: Optional[UUID] = None

class BlogPostRead(BlogPostBase):
    id: UUID
    content_html: str
    category_id: Optional[UUID]
    author_id: UUID
    published_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    reading_time_minutes: int = 0
    views: int = 0

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
    author: AuthorRead
    tags: List[TagRead] = []
    published_at: Optional[datetime] = None
    reading_time_minutes: int = Field(default=5, description="Estimated reading time in minutes")
    status: BlogStatus

    model_config = ConfigDict(from_attributes=True)

class BlogPagination(BaseModel):
    items: List[BlogPostShortRead]
    pageInfo: dict
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
