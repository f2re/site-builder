# Module: products/repository.py | Agent: backend-agent | Task: p_bugfix_backend_001
from datetime import datetime
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
        is_featured: Optional[bool] = None,
        cursor: Optional[str] = None, # Expect a cursor string "created_at,id"
        per_page: int = 20,
        active_only: bool = True,
    ) -> Tuple[list[dict], Optional[str]]:
        # Subqueries for prices and stock
        min_price_sq = (
            select(
                ProductVariant.product_id,
                func.min(ProductVariant.price).label("min_price")
            )
            .group_by(ProductVariant.product_id)
            .subquery()
        )

        stock_sq = (
            select(
                ProductVariant.product_id,
                func.coalesce(func.sum(ProductVariant.stock_quantity), 0).label("total_stock")
            )
            .group_by(ProductVariant.product_id)
            .subquery()
        )

        # Improved cover image subquery using window function
        # It picks is_cover=True first, then sorts by sort_order and id
        image_rank_sq = (
            select(
                ProductImage.product_id,
                ProductImage.url,
                func.row_number().over(
                    partition_by=ProductImage.product_id,
                    order_by=(
                        ProductImage.is_cover.desc(),
                        ProductImage.sort_order.asc(),
                        ProductImage.id.asc()
                    )
                ).label("rn")
            )
            .subquery()
        )
        
        cover_image_sq = (
            select(image_rank_sq.c.product_id, image_rank_sq.c.url)
            .where(image_rank_sq.c.rn == 1)
            .subquery()
        )

        stmt = (
            select(
                Product.id,
                Product.name,
                Product.slug,
                Product.category_id,
                Product.is_active,
                Product.is_featured,
                Product.created_at,
                Product.updated_at,
                cover_image_sq.c.url.label("main_image_url"),
                min_price_sq.c.min_price,
                stock_sq.c.total_stock,
            )
            .outerjoin(min_price_sq, Product.id == min_price_sq.c.product_id)
            .outerjoin(stock_sq, Product.id == stock_sq.c.product_id)
            .outerjoin(cover_image_sq, Product.id == cover_image_sq.c.product_id)
        )

        if active_only:
            stmt = stmt.where(Product.is_active)

        if category_id:
            stmt = stmt.where(Product.category_id == category_id)
        
        if is_featured is not None:
            stmt = stmt.where(Product.is_featured == is_featured)
        
        if min_price is not None:
            stmt = stmt.where(min_price_sq.c.min_price >= min_price)
        
        if max_price is not None:
            stmt = stmt.where(min_price_sq.c.min_price <= max_price)

        if cursor:
            try:
                cursor_created_at_str, cursor_id_str = cursor.split(',')
                cursor_created_at = datetime.fromisoformat(cursor_created_at_str.replace('Z', '+00:00'))
                cursor_id = UUID(cursor_id_str)
                # Keyset pagination condition
                stmt = stmt.where(
                    (Product.created_at > cursor_created_at) | 
                    ((Product.created_at == cursor_created_at) & (Product.id > cursor_id))
                )
            except (ValueError, IndexError):
                # Handle invalid cursor format gracefully
                pass

        stmt = stmt.order_by(Product.created_at, Product.id).limit(per_page + 1)
        
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
                "is_active": row.is_active,
                "is_featured": row.is_featured,
                "created_at": row.created_at,
                "updated_at": row.updated_at,
                "stock": int(row.total_stock or 0),
                "price_display": str(row.min_price.quantize(Decimal("0.01")) if row.min_price else Decimal("0.00")),
                "currency": "RUB",
            })
            
        next_cursor = None
        if len(rows) > per_page:
            last_item = items[-1]
            # Format the created_at to be URL-safe and consistent
            created_at_iso = last_item["created_at"].isoformat().replace('+00:00', 'Z')
            next_cursor = f"{created_at_iso},{last_item['id']}"
            
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
        return getattr(result, "rowcount", 0) > 0

    async def list_categories(self, active_only: bool = False) -> List[Category]:
        stmt = select(Category)
        if active_only:
            stmt = stmt.where(Category.is_active)
        stmt = stmt.order_by(Category.name)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_categories_tree(self) -> list[Category]:
        stmt = (
            select(Category)
            .where(Category.parent_id.is_(None))
            .options(selectinload(Category.children))
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_category_by_id(self, category_id: UUID) -> Optional[Category]:
        stmt = select(Category).where(Category.id == category_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_category(self, category: Category) -> Category:
        self.session.add(category)
        await self.session.flush()
        await self.session.refresh(category)
        return category

    async def update_category(self, category_id: UUID, **kwargs) -> Optional[Category]:
        if not kwargs:
            return await self.get_category_by_id(category_id)
        
        stmt = (
            update(Category)
            .where(Category.id == category_id)
            .values(**kwargs)
            .returning(Category)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def delete_category(self, category_id: UUID) -> bool:
        stmt = delete(Category).where(Category.id == category_id)
        result = await self.session.execute(stmt)
        return getattr(result, "rowcount", 0) > 0

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

    # Image Management
    async def add_image(self, product_id: UUID, url: str, alt: str = "", is_cover: bool = False) -> ProductImage:
        if is_cover:
            # Unset other cover images
            await self.session.execute(
                update(ProductImage)
                .where(ProductImage.product_id == product_id)
                .values(is_cover=False)
            )
            
        new_image = ProductImage(
            product_id=product_id,
            url=url,
            alt=alt,
            is_cover=is_cover
        )
        self.session.add(new_image)
        await self.session.flush()
        return new_image

    async def delete_image(self, image_id: UUID) -> Optional[ProductImage]:
        stmt = select(ProductImage).where(ProductImage.id == image_id)
        res = await self.session.execute(stmt)
        image = res.scalar_one_or_none()
        if image:
            await self.session.delete(image)
            await self.session.flush()
        return image

    async def set_cover_image(self, product_id: UUID, image_id: UUID) -> Optional[ProductImage]:
        # Unset other cover images
        await self.session.execute(
            update(ProductImage)
            .where(ProductImage.product_id == product_id)
            .values(is_cover=False)
        )
        
        stmt = (
            update(ProductImage)
            .where(ProductImage.id == image_id)
            .where(ProductImage.product_id == product_id)
            .values(is_cover=True)
            .returning(ProductImage)
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def count_images(self, product_id: UUID) -> int:
        stmt = select(func.count()).select_from(ProductImage).where(ProductImage.product_id == product_id)
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def has_cover_image(self, product_id: UUID) -> bool:
        stmt = select(ProductImage.id).where(ProductImage.product_id == product_id).where(ProductImage.is_cover == True).limit(1)  # noqa: E712
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None

async def get_product_repo(session: AsyncSession = Depends(get_db)) -> ProductRepository:
    return ProductRepository(session)
