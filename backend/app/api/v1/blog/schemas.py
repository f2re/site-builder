# Module: api/v1/blog/schemas.py | Agent: backend-agent | Task: phase3_backend_blog
from __future__ import annotations
from pydantic import BaseModel, ConfigDict, Field
from uuid import UUID
from datetime import datetime
from typing import List, Optional
from enum import Enum

class BlogStatus(str, Enum):
    draft = "draft"
    published = "published"
    archived = "archived"

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
    full_name: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class BlogPostBase(BaseModel):
    title: str
    slug: str
    summary: Optional[str] = None
    content: str
    status: BlogStatus
    is_featured: bool = False
    category_id: Optional[UUID] = None
    cover_image: Optional[str] = None
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None

class BlogPostCreate(BlogPostBase):
    pass

class BlogPostUpdate(BaseModel):
    title: Optional[str] = None
    slug: Optional[str] = None
    summary: Optional[str] = None
    content: Optional[str] = None
    status: Optional[BlogStatus] = None
    is_featured: Optional[bool] = None
    category_id: Optional[UUID] = None
    cover_image: Optional[str] = None
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None

class BlogPostRead(BlogPostBase):
    id: UUID
    category_id: Optional[UUID]
    author_id: UUID
    published_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
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
    reading_time_min: int = Field(default=5, description="Estimated reading time in minutes")
    
    model_config = ConfigDict(from_attributes=True)

class BlogPagination(BaseModel):
    items: List[BlogPostShortRead]
    next_cursor: Optional[str] = None
    total: int
