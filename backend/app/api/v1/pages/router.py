# Module: api/v1/pages/router.py | Agent: backend-agent | Task: p12_backend_001
from fastapi import APIRouter, Depends
from app.api.v1.pages.service import PageService, get_page_service
from app.api.v1.pages.schemas import PageRead


router = APIRouter(prefix="/pages", tags=["Static Pages"])


@router.get("/{slug}", response_model=PageRead)
async def get_page(
    slug: str,
    service: PageService = Depends(get_page_service)
):
    """Public endpoint to get page content by slug."""
    return await service.get_page_by_slug(slug, active_only=True)
