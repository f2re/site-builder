# Module: api/v1/pages/redirect_router.py | Agent: backend-agent | Task: p12_backend_001
from fastapi import APIRouter, Depends
from app.api.v1.pages.redirect_service import RedirectService, get_redirect_service
from app.api.v1.pages.schemas import RedirectRead


router = APIRouter(prefix="/redirects", tags=["Redirects"])


@router.get("/{path:path}", response_model=RedirectRead)
async def get_redirect(
    path: str,
    service: RedirectService = Depends(get_redirect_service)
):
    """Public endpoint to get redirect information by path."""
    return await service.get_redirect_by_path(path)
