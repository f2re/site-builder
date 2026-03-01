# Module: api/v1/pages/redirect_service.py | Agent: backend-agent | Task: p12_backend_001
from fastapi import Depends, HTTPException, status
from app.api.v1.pages.redirect_repository import RedirectRepository, get_redirect_repo
from app.db.models.redirect import Redirect


class RedirectService:
    def __init__(self, repo: RedirectRepository = Depends(get_redirect_repo)):
        self.repo = repo

    async def get_redirect_by_path(self, path: str) -> Redirect:
        """Find a redirect for the given path."""
        # Ensure path starts with /
        if not path.startswith("/"):
            path = "/" + path
            
        redirect = await self.repo.get_by_old_path(path)
        if not redirect:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Redirect not found"
            )
        return redirect


async def get_redirect_service(repo: RedirectRepository = Depends(get_redirect_repo)) -> RedirectService:
    return RedirectService(repo)
