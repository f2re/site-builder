# Module: products/repository.py | Agent: backend-agent | Task: bugfix_backend_category_count
from datetime import datetime
from typing import Optional, Tuple, List, Any
from uuid import UUID
from decimal import Decimal

from sqlalchemy import select, func, update, delete
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from app.db.models.product import (
    Product, Category, ProductVariant, ProductImage, StockMovement,
    ProductOptionGroup, ProductOptionValue
)
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
                selectinload(Product.variants),
                selectinload(Product.option_groups).selectinload(ProductOptionGroup.values)
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
                selectinload(Product.variants),
                selectinload(Product.option_groups).selectinload(ProductOptionGroup.values)
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_products(
        self,
        category_id: Optional[UUID] = None,
        category_slug: Optional[str] = None,
        min_price: Optional[Decimal] = None,
        max_price: Optional[Decimal] = None,
        is_featured: Optional[bool] = None,
        cursor: Optional[str] = None,  # Expect a cursor string "created_at,id"
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
                Category.name.label("category_name"),
            )
            .outerjoin(min_price_sq, Product.id == min_price_sq.c.product_id)
            .outerjoin(stock_sq, Product.id == stock_sq.c.product_id)
            .outerjoin(cover_image_sq, Product.id == cover_image_sq.c.product_id)
            .outerjoin(Category, Product.category_id == Category.id)
        )

        if active_only:
            stmt = stmt.where(Product.is_active)

        # category_id takes priority over category_slug
        if category_id:
            stmt = stmt.where(Product.category_id == category_id)
        elif category_slug:
            stmt = stmt.join(Category, Product.category_id == Category.id).where(
                Category.slug == category_slug
            )
        
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
            price = row.min_price if row.min_price is not None else Decimal(0)
            if price and price % 1 == 0:
                price_display = str(int(price))
            elif price:
                price_display = str(price.quantize(Decimal("0.01")))
            else:
                price_display = "0"
            items.append({
                "id": row.id,
                "name": row.name,
                "slug": row.slug,
                "category_id": row.category_id,
                "category_name": row.category_name,
                "main_image_url": row.main_image_url,
                "min_price": price,
                "is_active": row.is_active,
                "is_featured": row.is_featured,
                "created_at": row.created_at,
                "updated_at": row.updated_at,
                "stock": int(row.total_stock or 0),
                "price_display": price_display,
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

    async def list_categories(self, active_only: bool = False) -> List[dict[str, Any]]:
        # Define product count subquery
        count_stmt = select(Product.category_id, func.count(Product.id).label("cnt"))
        if active_only:
            count_stmt = count_stmt.where(Product.is_active.is_(True))
        
        count_sq = (
            count_stmt.group_by(Product.category_id)
            .subquery()
        )

        stmt = (
            select(
                Category,
                func.coalesce(count_sq.c.cnt, 0).label("product_count")
            )
            .outerjoin(count_sq, Category.id == count_sq.c.category_id)
        )
        if active_only:
            stmt = stmt.where(Category.is_active.is_(True))
        stmt = stmt.order_by(Category.name)
        
        result = await self.session.execute(stmt)
        items = []
        for row in result.all():
            cat = row.Category
            items.append({
                "id": cat.id,
                "name": cat.name,
                "slug": cat.slug,
                "is_active": cat.is_active,
                "parent_id": cat.parent_id,
                "product_count": row.product_count
            })
        return items

    async def get_categories_tree(self) -> list[dict[str, Any]]:
        # Count only active products
        count_sq = (
            select(Product.category_id, func.count(Product.id).label("cnt"))
            .where(Product.is_active.is_(True))
            .group_by(Product.category_id)
            .subquery()
        )

        # To build a tree with counts, we better fetch all categories and build it in memory
        # Or at least fetch them all with their counts.
        stmt = (
            select(
                Category,
                func.coalesce(count_sq.c.cnt, 0).label("product_count")
            )
            .outerjoin(count_sq, Category.id == count_sq.c.category_id)
        )
        
        result = await self.session.execute(stmt)
        all_cats = result.all()
        
        # Build mapping
        id_map = {}
        for row in all_cats:
            cat = row.Category
            id_map[cat.id] = {
                "id": cat.id,
                "name": cat.name,
                "slug": cat.slug,
                "is_active": cat.is_active,
                "parent_id": cat.parent_id,
                "product_count": row.product_count,
                "children": []
            }
            
        tree = []
        for cat_id, cat_data in id_map.items():
            parent_id = cat_data["parent_id"]
            if parent_id and parent_id in id_map:
                id_map[parent_id]["children"].append(cat_data)
            else:
                tree.append(cat_data)
        
        return tree

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

    async def update_image(self, image_id: UUID, **kwargs) -> Optional[ProductImage]:
        """Update an image record."""
        # Clean up data for update — only allow base fields
        update_fields = {k: v for k, v in kwargs.items() if k in ["alt", "is_cover", "sort_order", "url"]}
        if not update_fields:
            return None
        
        stmt = (
            update(ProductImage)
            .where(ProductImage.id == image_id)
            .values(**update_fields)
            .returning(ProductImage)
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def create_variant(self, product_id: UUID, **kwargs) -> ProductVariant:
        """Create a new variant for a product."""
        variant = ProductVariant(product_id=product_id, **kwargs)
        self.session.add(variant)
        await self.session.flush()
        return variant

    async def update_variant(self, variant_id: UUID, **kwargs) -> Optional[ProductVariant]:
        """Update a variant record."""
        # Clean up data for update
        update_fields = {k: v for k, v in kwargs.items() if k in ["name", "sku", "price", "stock_quantity", "attributes"]}
        if not update_fields:
            return None
            
        stmt = (
            update(ProductVariant)
            .where(ProductVariant.id == variant_id)
            .values(**update_fields)
            .returning(ProductVariant)
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    # ─── Option Groups ───
    async def create_option_group(self, product_id: UUID, **kwargs) -> ProductOptionGroup:
        group = ProductOptionGroup(product_id=product_id, **kwargs)
        self.session.add(group)
        await self.session.flush()
        return group

    async def get_option_group(self, group_id: UUID) -> Optional[ProductOptionGroup]:
        stmt = select(ProductOptionGroup).where(ProductOptionGroup.id == group_id).options(selectinload(ProductOptionGroup.values))
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def update_option_group(self, group_id: UUID, **kwargs) -> Optional[ProductOptionGroup]:
        stmt = update(ProductOptionGroup).where(ProductOptionGroup.id == group_id).values(**kwargs).returning(ProductOptionGroup)
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def delete_option_group(self, group_id: UUID) -> bool:
        stmt = delete(ProductOptionGroup).where(ProductOptionGroup.id == group_id)
        res = await self.session.execute(stmt)
        return getattr(res, "rowcount", 0) > 0

    # ─── Option Values ───
    async def create_option_value(self, group_id: UUID, **kwargs) -> ProductOptionValue:
        value = ProductOptionValue(group_id=group_id, **kwargs)
        self.session.add(value)
        await self.session.flush()
        return value

    async def get_option_value(self, value_id: UUID) -> Optional[ProductOptionValue]:
        stmt = select(ProductOptionValue).where(ProductOptionValue.id == value_id)
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def update_option_value(self, value_id: UUID, **kwargs) -> Optional[ProductOptionValue]:
        stmt = update(ProductOptionValue).where(ProductOptionValue.id == value_id).values(**kwargs).returning(ProductOptionValue)
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def delete_option_value(self, value_id: UUID) -> bool:
        stmt = delete(ProductOptionValue).where(ProductOptionValue.id == value_id)
        res = await self.session.execute(stmt)
        return getattr(res, "rowcount", 0) > 0

    async def get_option_values_by_ids(self, value_ids: List[UUID]) -> List[ProductOptionValue]:
        stmt = select(ProductOptionValue).where(ProductOptionValue.id.in_(value_ids)).options(selectinload(ProductOptionValue.group))
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

async def get_product_repo(session: AsyncSession = Depends(get_db)) -> ProductRepository:
    return ProductRepository(session)
