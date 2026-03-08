# Module: api/v1/orders/repository.py | Agent: backend-agent | Task: p22_backend_orders_date_filter
from datetime import date, datetime, timedelta
from typing import Optional, Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models.order import Order


class OrderRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, order: Order) -> Order:
        self.session.add(order)
        await self.session.flush()
        return order

    async def get_by_id(self, order_id: UUID) -> Optional[Order]:
        stmt = (
            select(Order)
            .where(Order.id == order_id)
            .options(
                selectinload(Order.items),
                selectinload(Order.user)
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_user_orders(self, user_id: UUID) -> Sequence[Order]:
        stmt = (
            select(Order)
            .where(Order.user_id == user_id)
            .options(
                selectinload(Order.items),
                selectinload(Order.user)
            )
            .order_by(Order.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def list_all(
        self,
        status: Optional[str] = None,
        offset: int = 0,
        limit: int = 20,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
    ) -> tuple[Sequence[Order], int]:
        from sqlalchemy import func
        stmt = (
            select(Order)
            .options(selectinload(Order.items), selectinload(Order.user))
            .order_by(Order.created_at.desc())
        )
        count_stmt = select(func.count()).select_from(Order)
        if status:
            status_lower = status.lower()
            stmt = stmt.where(Order.status == status_lower)
            count_stmt = count_stmt.where(Order.status == status_lower)
        if date_from:
            dt_from = datetime.combine(date_from, datetime.min.time())
            stmt = stmt.where(Order.created_at >= dt_from)
            count_stmt = count_stmt.where(Order.created_at >= dt_from)
        if date_to:
            dt_to = datetime.combine(date_to + timedelta(days=1), datetime.min.time())
            stmt = stmt.where(Order.created_at < dt_to)
            count_stmt = count_stmt.where(Order.created_at < dt_to)
        total = (await self.session.execute(count_stmt)).scalar() or 0
        stmt = stmt.offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all(), total

    async def update(self, order: Order) -> Order:
        await self.session.flush()
        return order

    async def get_by_cdek_uuid(self, cdek_uuid: str) -> Optional[Order]:
        stmt = select(Order).where(Order.cdek_order_uuid == cdek_uuid)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_tracking_number(self, tracking_number: str) -> Optional[Order]:
        stmt = select(Order).where(Order.tracking_number == tracking_number)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_orders_in_transit(self) -> Sequence[Order]:
        from app.db.models.order import OrderStatus
        stmt = (
            select(Order)
            .where(Order.status.in_([OrderStatus.SHIPPED, OrderStatus.PROCESSING]))
            .where(Order.tracking_number.isnot(None))
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()
