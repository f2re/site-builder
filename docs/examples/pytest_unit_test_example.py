"""
Эталонный unit-тест для backend-агента.
Reference-by-example: копируй структуру, не изобретай.
Документация: docs/examples/
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_session():
    """Мок AsyncSession — используй везде вместо реальной БД в unit-тестах."""
    session = AsyncMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    session.execute = AsyncMock()
    return session


@pytest.fixture
def product_data():
    return {"name": "OBD Adapter Pro", "price": 2990.0, "category_id": 1}


# ---------------------------------------------------------------------------
# Unit tests — Repository
# ---------------------------------------------------------------------------

class TestProductRepository:
    """Тесты репозитория: проверяем SQLAlchemy-запросы без бизнес-логики."""

    @pytest.mark.asyncio
    async def test_get_by_id_returns_product(self, mock_session):
        from app.api.v1.products.repository import ProductRepository
        from app.db.models.product import Product

        expected = Product(id=1, name="OBD Adapter", price=1990.0, category_id=1)
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = expected
        mock_session.execute.return_value = mock_result

        repo = ProductRepository(mock_session)
        result = await repo.get_by_id(1)

        assert result == expected
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_by_id_returns_none_for_missing(self, mock_session):
        from app.api.v1.products.repository import ProductRepository

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        repo = ProductRepository(mock_session)
        result = await repo.get_by_id(999)

        assert result is None

    @pytest.mark.asyncio
    async def test_create_calls_commit_and_refresh(self, mock_session, product_data):
        from app.api.v1.products.repository import ProductRepository
        from app.api.v1.products.schemas import ProductCreate

        repo = ProductRepository(mock_session)
        data = ProductCreate(**product_data)
        await repo.create(data)

        mock_session.add.assert_called_once()
        mock_session.commit.assert_awaited_once()
        mock_session.refresh.assert_awaited_once()


# ---------------------------------------------------------------------------
# Unit tests — Service
# ---------------------------------------------------------------------------

class TestProductService:
    """Тесты бизнес-логики: мокаем репозиторий, тестируем оркестрацию."""

    @pytest.mark.asyncio
    async def test_get_or_404_raises_on_missing(self, mock_session):
        from app.api.v1.products.service import ProductService

        with patch(
            "app.api.v1.products.service.ProductRepository.get_by_id",
            new_callable=AsyncMock,
            return_value=None,
        ):
            service = ProductService(mock_session)
            with pytest.raises(HTTPException) as exc:
                await service.get_or_404(999)
            assert exc.value.status_code == 404

    @pytest.mark.asyncio
    async def test_list_products_returns_paginated_response(self, mock_session):
        from app.api.v1.products.service import ProductService
        from app.db.models.product import Product

        mock_products = [
            Product(id=1, name="A", price=1000.0, category_id=1),
            Product(id=2, name="B", price=2000.0, category_id=1),
        ]

        with patch(
            "app.api.v1.products.service.ProductRepository.get_list",
            new_callable=AsyncMock,
            return_value=(mock_products, 2),
        ):
            service = ProductService(mock_session)
            result = await service.list_products(page=1, size=20)

        assert result.total == 2
        assert len(result.items) == 2
        assert result.page == 1
