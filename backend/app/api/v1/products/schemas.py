# Module: api/v1/products/schemas.py | Agent: backend-agent | Task: bugfix_backend_category_count
from __future__ import annotations
from pydantic import BaseModel, ConfigDict, Field, model_validator
from uuid import UUID
from datetime import datetime
from typing import List, Optional, Any
from decimal import Decimal


class ProductOptionValueSchema(BaseModel):
    id: UUID
    name: str
    price_modifier: Decimal
    is_default: bool
    sort_order: int
    sku_suffix: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class ProductOptionValueCreate(BaseModel):
    name: str
    price_modifier: Decimal = Decimal("0")
    is_default: bool = False
    sort_order: int = 0
    sku_suffix: Optional[str] = None


class ProductOptionValueUpdate(BaseModel):
    name: Optional[str] = None
    price_modifier: Optional[Decimal] = None
    is_default: Optional[bool] = None
    sort_order: Optional[int] = None
    sku_suffix: Optional[str] = None


class ProductOptionGroupSchema(BaseModel):
    id: UUID
    name: str
    type: str = "radio"
    is_required: bool
    sort_order: int
    values: List[ProductOptionValueSchema] = []
    model_config = ConfigDict(from_attributes=True)


class ProductOptionGroupCreate(BaseModel):
    name: str
    type: str = "radio"
    is_required: bool = True
    sort_order: int = 0


class ProductOptionGroupUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    is_required: Optional[bool] = None
    sort_order: Optional[int] = None


class ProductPriceCalculationRequest(BaseModel):
    product_id: UUID
    selected_option_value_ids: List[UUID] = []


class ProductPriceCalculationResponse(BaseModel):
    product_id: UUID
    base_price: Decimal
    total_modifier: Decimal
    final_price: Decimal
    breakdown: List[dict] = Field(
        default_factory=list,
        description="List of {group_name, value_name, price_modifier}",
    )

class CategoryBase(BaseModel):
    name: str
    slug: Optional[str] = None
    is_active: bool = True
    parent_id: Optional[UUID] = None

class CategoryRead(CategoryBase):
    id: UUID
    slug: str  # Mandatory in Read
    product_count: int = 0
    model_config = ConfigDict(from_attributes=True)

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    is_active: Optional[bool] = None
    parent_id: Optional[UUID] = None

class CategoryTreeRead(CategoryRead):
    children: List[CategoryTreeRead] = []

class ProductImageBase(BaseModel):
    url: str
    alt: str
    is_cover: bool = False
    sort_order: int = 0
    width: Optional[int] = None
    height: Optional[int] = None

class ProductImageRead(ProductImageBase):
    id: UUID
    sequence: int = 1
    base_path: Optional[str] = None
    formats: dict = Field(default_factory=dict)
    model_config = ConfigDict(from_attributes=True)

class ProductVariantBase(BaseModel):
    name: str
    sku: str
    price: Decimal
    stock_quantity: int = 0
    attributes: dict[str, Any] = Field(default_factory=lambda: {})

class ProductVariantRead(ProductVariantBase):
    id: UUID
    model_config = ConfigDict(from_attributes=True)

class ProductVariantUpdate(ProductVariantBase):
    """Schema for updating variants via PUT /admin/products/{id}.
    id is optional: if provided — update existing variant; if None — create new one."""
    id: Optional[UUID] = None

class StockMovementRead(BaseModel):
    id: UUID
    variant_id: UUID
    delta: int
    reason: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class ProductBase(BaseModel):
    category_id: Optional[UUID] = None
    name: str
    slug: Optional[str] = None
    description: Optional[str] = None
    description_html: Optional[str] = None
    content_json: Any = Field(default_factory=lambda: {}, description="TipTap JSON content")
    meta_title: Optional[str] = Field(None, max_length=255)
    meta_description: Optional[str] = Field(None, max_length=500)
    og_image_url: Optional[str] = None
    doc_iframe_url: Optional[str] = None
    attributes: dict[str, Any] = Field(default_factory=lambda: {})
    is_active: bool = True
    is_featured: bool = False

class ProductRead(ProductBase):
    id: UUID
    slug: str  # Mandatory in Read
    created_at: datetime
    updated_at: datetime
    category: Optional[CategoryRead] = None
    images: List[ProductImageRead] = []
    variants: List[ProductVariantRead] = []
    option_groups: List[ProductOptionGroupSchema] = []
    stock: int = 0
    model_config = ConfigDict(from_attributes=True)


    @model_validator(mode="after")
    def compute_stock(self) -> "ProductRead":
        self.stock = sum(v.stock_quantity for v in self.variants)
        return self

class ProductCreate(ProductBase):
    images: List[ProductImageBase] = []
    variants: List[ProductVariantBase] = []

class ProductUpdate(BaseModel):
    category_id: Optional[UUID] = None
    name: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None
    description_html: Optional[str] = None
    content_json: Optional[Any] = None
    meta_title: Optional[str] = Field(None, max_length=255)
    meta_description: Optional[str] = Field(None, max_length=500)
    og_image_url: Optional[str] = None
    doc_iframe_url: Optional[str] = None
    attributes: Optional[dict[str, Any]] = None
    is_active: Optional[bool] = None
    is_featured: Optional[bool] = None
    images: Optional[List[ProductImageRead]] = None
    variants: Optional[List[ProductVariantUpdate]] = None

class ProductShortRead(BaseModel):
    id: UUID
    name: str
    slug: str
    category_id: Optional[UUID]
    category_name: Optional[str] = None
    main_image_url: Optional[str] = None
    min_price: Decimal
    is_active: bool
    is_featured: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    stock: int = 0
    price_display: str = ""
    currency: str = "RUB"
    has_price_modifiers: bool = False
    model_config = ConfigDict(from_attributes=True)

class PaginatedResponse(BaseModel):
    next_cursor: Optional[str] = None
    per_page: int

class ProductPagination(PaginatedResponse):
    items: List[ProductShortRead]

class CategoryListResponse(BaseModel):
    items: List[CategoryTreeRead]
