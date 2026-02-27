# Module: api/v1/products/repository.py | Agent: backend-agent | Task: BE-01
from typing import Optional, Tuple, List
from uuid import UUID
from decimal import Decimal

from sqlalchemy import select, func, update, delete
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from app.db.models.product import Product, Category, ProductVariant, ProductImage, StockMovement
from app.db.session import get_db

class ProductRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, product_id: UUID) -> Optional[Product]:
        stmt = (
            select(Product)
            .where(Product.id == product_id)
            .options(
                selectinload(Product.category),
                selectinload(Product.images),
                selectinload(Product.variants)
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_slug(self, slug: str) -> Optional[Product]:
        stmt = (
            select(Product)
            .where(Product.slug == slug)
            .options(
                selectinload(Product.category),
                selectinload(Product.images),
                selectinload(Product.variants)
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_products(
        self,
        category_id: Optional[UUID] = None,
        min_price: Optional[Decimal] = None,
        max_price: Optional[Decimal] = None,
        cursor: Optional[UUID] = None,
        per_page: int = 20,
    ) -> Tuple[list[dict], Optional[str]]:
        # Subqueries for prices and cover images
        min_price_sq = (
            select(
                ProductVariant.product_id,
                func.min(ProductVariant.price).label("min_price")
            )
            .group_by(ProductVariant.product_id)
            .subquery()
        )
        
        cover_image_sq = (
            select(
                ProductImage.product_id,
                ProductImage.url
            )
            .where(ProductImage.is_cover)
            .subquery()
        )

        stmt = (
            select(
                Product.id,
                Product.name,
                Product.slug,
                Product.category_id,
                Product.is_active,
                cover_image_sq.c.url.label("main_image_url"),
                min_price_sq.c.min_price
            )
            .outerjoin(min_price_sq, Product.id == min_price_sq.c.product_id)
            .outerjoin(cover_image_sq, Product.id == cover_image_sq.c.product_id)
            .where(Product.is_active)
        )

        if category_id:
            stmt = stmt.where(Product.category_id == category_id)
        
        if min_price is not None:
            stmt = stmt.where(min_price_sq.c.min_price >= min_price)
        
        if max_price is not None:
            stmt = stmt.where(min_price_sq.c.min_price <= max_price)

        if cursor:
            stmt = stmt.where(Product.id > cursor)
        
        stmt = stmt.order_by(Product.id).limit(per_page + 1)
        
        result = await self.session.execute(stmt)
        rows = result.all()
        
        items = []
        for row in rows[:per_page]:
            items.append({
                "id": row.id,
                "name": row.name,
                "slug": row.slug,
                "category_id": row.category_id,
                "main_image_url": row.main_image_url,
                "min_price": row.min_price if row.min_price is not None else Decimal(0),
                "is_active": row.is_active
            })
            
        next_cursor = None
        if len(rows) > per_page:
            next_cursor = str(items[-1]["id"])
            
        return items, next_cursor

    async def create(self, product: Product) -> Product:
        """Create a new product."""
        self.session.add(product)
        await self.session.flush()
        await self.session.refresh(product)
        return product

    async def update(self, product_id: UUID, **kwargs) -> Optional[Product]:
        """Update a product with partial data."""
        if not kwargs:
            return await self.get_by_id(product_id)

        stmt = (
            update(Product)
            .where(Product.id == product_id)
            .values(**kwargs)
            .returning(Product)
        )
        result = await self.session.execute(stmt)
        updated_product = result.scalar_one_or_none()
        
        if updated_product:
            return await self.get_by_id(product_id)
        
        return None

    async def delete(self, product_id: UUID) -> bool:
        """Delete a product."""
        stmt = delete(Product).where(Product.id == product_id)
        result = await self.session.execute(stmt)
        return result.rowcount > 0

    async def get_categories_tree(self) -> list[Category]:
        stmt = (
            select(Category)
            .where(Category.parent_id.is_(None))
            .options(selectinload(Category.children))
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def decrement_stock(self, variant_id: UUID, quantity: int, reason: str = "order") -> bool:
        """
        Atomic stock decrement in DB. 
        Note: Real-time stock reservation should be done in Redis.
        """
        stmt = (
            update(ProductVariant)
            .where(ProductVariant.id == variant_id)
            .where(ProductVariant.stock_quantity >= quantity)
            .values(stock_quantity=ProductVariant.stock_quantity - quantity)
            .returning(ProductVariant.id)
        )
        result = await self.session.execute(stmt)
        updated = result.scalar_one_or_none()
        
        if updated:
            movement = StockMovement(
                variant_id=variant_id,
                delta=-quantity,
                reason=reason
            )
            self.session.add(movement)
            await self.session.flush()
            return True
        return False

    async def increment_stock(self, variant_id: UUID, quantity: int, reason: str = "restock") -> bool:
        stmt = (
            update(ProductVariant)
            .where(ProductVariant.id == variant_id)
            .values(stock_quantity=ProductVariant.stock_quantity + quantity)
            .returning(ProductVariant.id)
        )
        result = await self.session.execute(stmt)
        updated = result.scalar_one_or_none()
        
        if updated:
            movement = StockMovement(
                variant_id=variant_id,
                delta=quantity,
                reason=reason
            )
            self.session.add(movement)
            await self.session.flush()
            return True
        return False

async def get_product_repo(session: AsyncSession = Depends(get_db)) -> ProductRepository:
    return ProductRepository(session)
