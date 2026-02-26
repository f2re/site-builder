from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.v1.blog.schemas import BlogPagination, BlogPostRead, BlogCategoryRead
from app.api.v1.blog.repository import BlogRepository, get_blog_repo
from app.db.models.blog import BlogStatus

router = APIRouter(prefix="/blog", tags=["Blog"])

@router.get("/posts", response_model=BlogPagination)
async def list_posts(
    category_slug: Optional[str] = Query(None, description="Filter by category slug"),
    tag_slug: Optional[str] = Query(None, description="Filter by tag slug"),
    cursor: Optional[UUID] = Query(None, description="Cursor for pagination"),
    per_page: int = Query(20, ge=1, le=100),
    repo: BlogRepository = Depends(get_blog_repo)
):
    """
    List published blog posts with filtering and pagination.
    """
    items, next_cursor, total = await repo.list_posts(
        category_slug=category_slug,
        tag_slug=tag_slug,
        status=BlogStatus.published,
        cursor=cursor,
        per_page=per_page
    )
    return {
        "items": items,
        "next_cursor": next_cursor,
        "total": total
    }

@router.get("/posts/{slug}", response_model=BlogPostRead)
async def get_post(
    slug: str,
    repo: BlogRepository = Depends(get_blog_repo)
):
    """
    Get a single published blog post by its slug.
    """
    post = await repo.get_by_slug(slug, status=BlogStatus.published)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    return post

@router.get("/categories", response_model=List[BlogCategoryRead])
async def list_categories(
    repo: BlogRepository = Depends(get_blog_repo)
):
    """
    Get all blog categories.
    """
    return await repo.get_categories()
