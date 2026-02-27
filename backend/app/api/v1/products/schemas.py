# Module: api/v1/products/schemas.py | Agent: backend-agent | Task: product_service_crud
from __future__ import annotations
from pydantic import BaseModel, ConfigDict, Field
from uuid import UUID
from datetime import datetime
from typing import List, Optional, Any
from decimal import Decimal

class CategoryBase(BaseModel):
    name: str
    slug: str
    parent_id: Optional[UUID] = None

class CategoryRead(CategoryBase):
    id: UUID
    model_config = ConfigDict(from_attributes=True)

class CategoryTreeRead(CategoryRead):
    children: List[CategoryTreeRead] = []

class ProductImageRead(BaseModel):
    id: UUID
    url: str
    is_main: bool
    position: int
    model_config = ConfigDict(from_attributes=True)

class ProductVariantRead(BaseModel):
    id: UUID
    sku: str
    price: Decimal
    stock_quantity: int
    attributes: dict[str, Any]
    model_config = ConfigDict(from_attributes=True)

class ProductRead(BaseModel):
    id: UUID
    category_id: Optional[UUID]
    name: str
    slug: str
    description: Optional[str] = None
    attributes: dict[str, Any]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    category: Optional[CategoryRead] = None
    images: List[ProductImageRead] = []
    variants: List[ProductVariantRead] = []
    model_config = ConfigDict(from_attributes=True)

class ProductCreate(BaseModel):
    category_id: Optional[UUID] = None
    name: str
    slug: str
    description: Optional[str] = None
    attributes: dict[str, Any] = Field(default_factory=dict)
    is_active: bool = True

class ProductUpdate(BaseModel):
    category_id: Optional[UUID] = None
    name: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None
    attributes: Optional[dict[str, Any]] = None
    is_active: Optional[bool] = None

class ProductShortRead(BaseModel):
    id: UUID
    name: str
    slug: str
    category_id: Optional[UUID]
    main_image_url: Optional[str] = None
    min_price: Decimal
    is_active: bool
    model_config = ConfigDict(from_attributes=True)

class PaginatedResponse(BaseModel):
    next_cursor: Optional[str] = None
    per_page: int

class ProductPagination(PaginatedResponse):
    items: List[ProductShortRead]
