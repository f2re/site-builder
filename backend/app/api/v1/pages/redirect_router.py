# Module: api/v1/pages/redirect_router.py | Agent: backend-agent | Task: p15_backend_redirect_fix
from fastapi import APIRouter, Depends, Query
from app.api.v1.pages.redirect_service import RedirectService, get_redirect_service
from app.api.v1.pages.schemas import RedirectRead
from app.db.models.redirect import Redirect


router = APIRouter(prefix="/redirects", tags=["Redirects"])


@router.get("/lookup", response_model=RedirectRead)
async def lookup_redirect(
    old_path: str = Query(
        ...,
        description=(
            "Full old path including query string, "
            "e.g. /index.php?route=product/category&path=61_67"
        ),
    ),
    service: RedirectService = Depends(get_redirect_service),
) -> Redirect:
    """Lookup a redirect by full path including query string.

    Unlike the /{path:path} endpoint, this endpoint accepts the complete
    old_path (with query string) as a query parameter, which avoids the
    FastAPI limitation where path parameters capture only the URL path
    segment before '?'.
    """
    return await service.get_redirect_by_path(old_path)


@router.get("/{path:path}", response_model=RedirectRead)
async def get_redirect(
    path: str,
    service: RedirectService = Depends(get_redirect_service),
) -> Redirect:
    """Lookup a redirect by path (without query string).

    For paths that contain a query string, use GET /redirects/lookup?old_path=...
    instead, because FastAPI path parameters do not capture query strings.
    """
    return await service.get_redirect_by_path(path)
