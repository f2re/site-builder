# Эталонный endpoint — router/service/repository/schemas

> Reference-by-example: копируй паттерн вместо интерпретации правил.
> Источник: docs/examples/ (уровень 5 иерархии истины)

---

## Структура файлов

```
backend/app/api/v1/<feature>/
├── router.py      ← FastAPI Router, только HTTP-логика
├── service.py     ← Бизнес-логика, оркестрация
├── repository.py  ← SQLAlchemy запросы, без бизнес-логики
└── schemas.py     ← Pydantic I/O схемы
```

---

## schemas.py

```python
from pydantic import BaseModel, ConfigDict
from datetime import datetime


class ProductBase(BaseModel):
    name: str
    price: float
    category_id: int


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: str | None = None
    price: float | None = None


class ProductResponse(ProductBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProductListResponse(BaseModel):
    items: list[ProductResponse]
    total: int
    page: int
    size: int
```

---

## repository.py

```python
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.product import Product
from .schemas import ProductCreate, ProductUpdate


class ProductRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, product_id: int) -> Product | None:
        result = await self.session.execute(
            select(Product).where(Product.id == product_id)
        )
        return result.scalar_one_or_none()

    async def get_list(
        self, page: int = 1, size: int = 20, category_id: int | None = None
    ) -> tuple[list[Product], int]:
        query = select(Product)
        if category_id:
            query = query.where(Product.category_id == category_id)

        total_result = await self.session.execute(
            select(func.count()).select_from(query.subquery())
        )
        total = total_result.scalar_one()

        result = await self.session.execute(
            query.offset((page - 1) * size).limit(size)
        )
        return result.scalars().all(), total

    async def create(self, data: ProductCreate) -> Product:
        product = Product(**data.model_dump())
        self.session.add(product)
        await self.session.commit()
        await self.session.refresh(product)
        return product

    async def update(self, product: Product, data: ProductUpdate) -> Product:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(product, field, value)
        await self.session.commit()
        await self.session.refresh(product)
        return product
```

---

## service.py

```python
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from .repository import ProductRepository
from .schemas import ProductCreate, ProductUpdate, ProductResponse, ProductListResponse


class ProductService:
    def __init__(self, session: AsyncSession):
        self.repo = ProductRepository(session)

    async def get_or_404(self, product_id: int):
        product = await self.repo.get_by_id(product_id)
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
        return product

    async def list_products(
        self, page: int = 1, size: int = 20, category_id: int | None = None
    ) -> ProductListResponse:
        items, total = await self.repo.get_list(page, size, category_id)
        return ProductListResponse(
            items=items, total=total, page=page, size=size
        )

    async def create_product(self, data: ProductCreate) -> ProductResponse:
        product = await self.repo.create(data)
        return ProductResponse.model_validate(product)

    async def update_product(self, product_id: int, data: ProductUpdate) -> ProductResponse:
        product = await self.get_or_404(product_id)
        product = await self.repo.update(product, data)
        return ProductResponse.model_validate(product)
```

---

## router.py

```python
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.dependencies import get_db, get_current_user
from app.db.models.user import User
from .service import ProductService
from .schemas import ProductCreate, ProductUpdate, ProductResponse, ProductListResponse

router = APIRouter(prefix="/products", tags=["products"])


@router.get("/", response_model=ProductListResponse)
async def list_products(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    category_id: int | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    service = ProductService(db)
    return await service.list_products(page, size, category_id)


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: int,
    db: AsyncSession = Depends(get_db),
):
    service = ProductService(db)
    return await service.get_or_404(product_id)


@router.post("/", response_model=ProductResponse, status_code=201)
async def create_product(
    data: ProductCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ProductService(db)
    return await service.create_product(data)


@router.patch("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    data: ProductUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ProductService(db)
    return await service.update_product(product_id, data)
```
