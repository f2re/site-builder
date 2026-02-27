from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from uuid import UUID

from app.core.dependencies import get_current_user, require_admin
from app.db.models.user import User
from .schemas import (
    BlogPagination,
    BlogPostRead,
    BlogPostCreate,
    BlogPostUpdate,
    BlogStatus
)
from .service import BlogService, get_blog_service

router = APIRouter(prefix="/blog", tags=["Blog"])


@router.get("/posts", response_model=BlogPagination)
async def list_posts(
    status: Optional[BlogStatus] = Query(BlogStatus.published, description="Filter by status: draft|published|archived"),
    category: Optional[str] = Query(None, description="Filter by category slug"),
    tag: Optional[str] = Query(None, description="Filter by tag slug"),
    after: Optional[UUID] = Query(None, description="Cursor for pagination"),
    limit: int = Query(12, ge=1, le=100),
    service: BlogService = Depends(get_blog_service),
):
    """List blog posts with pagination and filters."""
    return await service.list_posts(
        status=status,
        category_slug=category,
        tag_slug=tag,
        cursor=after,
        per_page=limit,
    )


@router.get("/posts/{slug}", response_model=BlogPostRead)
async def get_post(
    slug: str,
    service: BlogService = Depends(get_blog_service),
):
    """Get single blog post by slug. Increments views."""
    return await service.get_post_detail(slug)


@router.get("/categories")
async def list_categories(service: BlogService = Depends(get_blog_service)):
    """List all blog categories."""
    return await service.list_categories()


# Admin endpoints
@router.post("/posts", response_model=BlogPostRead, dependencies=[Depends(require_admin)])
async def create_post(
    data: BlogPostCreate,
    current_user: User = Depends(get_current_user),
    service: BlogService = Depends(get_blog_service),
):
    """Create new blog post (admin only)."""
    return await service.create_post(data, author_id=current_user.id)


@router.put("/posts/{post_id}", response_model=BlogPostRead, dependencies=[Depends(require_admin)])
async def update_post(
    post_id: UUID,
    data: BlogPostUpdate,
    service: BlogService = Depends(get_blog_service),
):
    """Update blog post (admin only)."""
    return await service.update_post(post_id, data)


@router.delete("/posts/{post_id}", dependencies=[Depends(require_admin)])
async def delete_post(
    post_id: UUID,
    service: BlogService = Depends(get_blog_service),
):
    """Delete (archive) blog post (admin only)."""
    success = await service.delete_post(post_id)
    if not success:
        raise HTTPException(status_code=404, detail="Post not found")
    return {"message": "Post deleted"}
