# Module: api/v1/admin/pages_router.py | Agent: backend-agent | Task: p12_backend_001
from uuid import UUID
from typing import List
from fastapi import APIRouter, Depends, status

from app.api.v1.pages.service import PageService, get_page_service
from app.api.v1.pages.schemas import PageRead, PageCreate, PageUpdate
from app.core.dependencies import require_admin
from app.db.models.user import User

router = APIRouter(prefix="/pages", tags=["Admin Static Pages"])

# Admin dependency for all routes in this router
AdminDep = Depends(require_admin)

@router.get("", response_model=List[PageRead])
async def list_pages(
    _admin: User = AdminDep,
    service: PageService = Depends(get_page_service)
):
    """Admin endpoint to list all pages (including inactive)."""
    return await service.list_all_pages(active_only=False)

@router.post("", response_model=PageRead, status_code=status.HTTP_201_CREATED)
async def create_page(
    payload: PageCreate,
    _admin: User = AdminDep,
    service: PageService = Depends(get_page_service)
):
    """Admin endpoint to create a new static page."""
    return await service.create_page(payload)

@router.get("/{page_id}", response_model=PageRead)
async def get_page(
    page_id: UUID,
    _admin: User = AdminDep,
    service: PageService = Depends(get_page_service)
):
    """Admin endpoint to get page details by ID."""
    return await service.get_page_by_id(page_id)

@router.patch("/{page_id}", response_model=PageRead)
async def update_page(
    page_id: UUID,
    payload: PageUpdate,
    _admin: User = AdminDep,
    service: PageService = Depends(get_page_service)
):
    """Admin endpoint to update an existing static page."""
    return await service.update_page(page_id, payload)

@router.delete("/{page_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_page(
    page_id: UUID,
    _admin: User = AdminDep,
    service: PageService = Depends(get_page_service)
):
    """Admin endpoint to delete a static page."""
    await service.delete_page(page_id)
