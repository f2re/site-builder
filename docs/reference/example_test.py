# Module: tests/unit/api/test_products | Agent: testing-agent | Task: p3_testing_001
"""
Example unit test for FastAPI endpoint.
Uses dependency_overrides to mock services.
"""
from uuid import uuid4
import pytest
from fastapi import status
from httpx import AsyncClient
from app.api.v1.products.schemas import ProductResponse
from app.main import app

@pytest.mark.asyncio
async def test_get_product_not_found(client: AsyncClient):
    """
    Test that GET /products/{id} returns 404 if product doesn't exist.
    """
    product_id = uuid4()
    response = await client.get(f"/api/v1/products/{product_id}")
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Product not found"

@pytest.mark.asyncio
async def test_get_product_success(client: AsyncClient, mock_product):
    """
    Test that GET /products/{id} returns product if it exists.
    """
    response = await client.get(f"/api/v1/products/{mock_product.id}")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == str(mock_product.id)
    assert data["name"] == mock_product.name
    # Verify response schema contract
    ProductResponse.model_validate(data)
