# Module: api/v1/pages/service.py | Agent: backend-agent | Task: p12_backend_001
from typing import Sequence
from uuid import UUID
from fastapi import Depends, HTTPException, status
from app.api.v1.pages.repository import PageRepository, get_page_repo
from app.api.v1.pages.schemas import PageCreate, PageUpdate
from app.db.models.page import StaticPage


class PageService:
    def __init__(self, repo: PageRepository = Depends(get_page_repo)):
        self.repo = repo

    async def get_page_by_slug(self, slug: str, active_only: bool = True) -> StaticPage:
        page = await self.repo.get_by_slug(slug, active_only=active_only)
        if not page:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Page not found"
            )
        return page

    async def list_all_pages(self, active_only: bool = False) -> Sequence[StaticPage]:
        return await self.repo.list_all(active_only=active_only)

    async def get_page_by_id(self, page_id: UUID) -> StaticPage:
        page = await self.repo.get_by_id(page_id)
        if not page:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Page not found"
            )
        return page

    async def create_page(self, data: PageCreate) -> StaticPage:
        # Check if slug exists
        existing = await self.repo.get_by_slug(data.slug)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Page with slug '{data.slug}' already exists"
            )
        
        page = StaticPage(**data.model_dump())
        return await self.repo.create(page)

    async def update_page(self, page_id: UUID, data: PageUpdate) -> StaticPage:
        update_data = data.model_dump(exclude_unset=True)
        if "slug" in update_data:
            existing = await self.repo.get_by_slug(update_data["slug"])
            if existing and existing.id != page_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Page with slug '{update_data['slug']}' already exists"
                )
        
        page = await self.repo.update(page_id, **update_data)
        if not page:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Page not found"
            )
        return page

    async def delete_page(self, page_id: UUID) -> None:
        success = await self.repo.delete(page_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Page not found"
            )


async def get_page_service(repo: PageRepository = Depends(get_page_repo)) -> PageService:
    return PageService(repo)
