from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.db.session import get_db
from app.core.dependencies import get_current_user, require_admin
from app.db.models.user import User
from .schemas import (
    BlogPostListResponse,
    BlogPostDetailResponse,
    BlogPostCreate,
    BlogPostUpdate,
)
from .service import BlogService

router = APIRouter(prefix="/blog", tags=["Blog"])


@router.get("/posts", response_model=BlogPostListResponse)
async def list_posts(
    status: str | None = Query(None, description="Filter by status: draft|published|archived"),
    category: str | None = Query(None, description="Filter by category slug"),
    tag: str | None = Query(None, description="Filter by tag slug"),
    after: str | None = Query(None, description="Cursor for pagination"),
    limit: int = Query(12, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """List blog posts with pagination and filters."""
    service = BlogService(db)
    return await service.list_posts(
        status=status,
        category=category,
        tag=tag,
        after=after,
        limit=limit,
    )


@router.get("/posts/{slug}", response_model=BlogPostDetailResponse)
async def get_post(
    slug: str,
    db: AsyncSession = Depends(get_db),
):
    """Get single blog post by slug. Increments views."""
    service = BlogService(db)
    post = await service.get_post_by_slug(slug)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


@router.get("/categories")
async def list_categories(db: AsyncSession = Depends(get_db)):
    """List all blog categories."""
    service = BlogService(db)
    return await service.list_categories()


@router.get("/tags")
async def list_tags(db: AsyncSession = Depends(get_db)):
    """List all tags."""
    service = BlogService(db)
    return await service.list_tags()


# Admin endpoints
@router.post("/posts", response_model=BlogPostDetailResponse, dependencies=[Depends(require_admin)])
async def create_post(
    data: BlogPostCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create new blog post (admin only)."""
    service = BlogService(db)
    return await service.create_post(data, author_id=current_user.id)


@router.put("/posts/{post_id}", response_model=BlogPostDetailResponse, dependencies=[Depends(require_admin)])
async def update_post(
    post_id: int,
    data: BlogPostUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update blog post (admin only)."""
    service = BlogService(db)
    post = await service.update_post(post_id, data)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


@router.delete("/posts/{post_id}", dependencies=[Depends(require_admin)])
async def delete_post(
    post_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Delete (archive) blog post (admin only)."""
    service = BlogService(db)
    success = await service.delete_post(post_id)
    if not success:
        raise HTTPException(status_code=404, detail="Post not found")
    return {"message": "Post deleted"}
