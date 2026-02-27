# Module: api/v1/blog/router.py | Agent: backend-agent | Task: BE-02
from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import List, Optional, Union
from uuid import UUID

from app.core.dependencies import get_current_user, require_role
from app.db.models.user import User
from app.db.models.blog import BlogPostStatus
from .schemas import (
    BlogPagination,
    BlogPostRead,
    BlogPostCreate,
    BlogPostUpdate,
    BlogStatus,
    CommentCreate,
    CommentRead,
    CommentAdminRead,
    TagRead
)
from .service import BlogService, get_blog_service

router = APIRouter(prefix="/blog", tags=["Blog"])


@router.get("/posts", response_model=BlogPagination)
async def list_posts(
    status: Optional[BlogPostStatus] = Query(BlogPostStatus.PUBLISHED, description="Filter by status: DRAFT|PUBLISHED|ARCHIVED"),
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
    """Get single blog post by slug."""
    return await service.get_post_detail(slug)


@router.get("/categories")
async def list_categories(service: BlogService = Depends(get_blog_service)):
    """List all blog categories."""
    return await service.list_categories()


@router.get("/tags", response_model=List[TagRead])
async def list_tags(service: BlogService = Depends(get_blog_service)):
    """List all unique tags."""
    return await service.get_tags()


@router.post("/posts/{post_id}/comments", response_model=CommentRead, status_code=status.HTTP_201_CREATED)
async def create_comment(
    post_id: UUID,
    data: CommentCreate,
    service: BlogService = Depends(get_blog_service),
):
    """Publicly post a comment (pending approval)."""
    return await service.create_comment(post_id, data)


@router.get("/posts/{post_id}/comments", response_model=Union[List[CommentRead], List[CommentAdminRead]])
async def list_comments(
    post_id: UUID,
    current_user: Optional[User] = Depends(get_current_user),
    service: BlogService = Depends(get_blog_service),
):
    """List approved comments for a post (Admins see all and decrypted emails)."""
    is_admin = current_user.role == "admin" if current_user else False
    return await service.get_comments(post_id, is_admin=is_admin)


# Admin endpoints
@router.post("/posts", response_model=BlogPostRead, status_code=status.HTTP_201_CREATED)
async def create_post(
    data: BlogPostCreate,
    current_user: User = Depends(require_role("admin")),
    service: BlogService = Depends(get_blog_service),
):
    """Create new blog post (admin only)."""
    return await service.create_post(data, user_id=current_user.id)


@router.put("/posts/{post_id}", response_model=BlogPostRead)
async def update_post(
    post_id: UUID,
    data: BlogPostUpdate,
    current_user: User = Depends(require_role("admin")),
    service: BlogService = Depends(get_blog_service),
):
    """Update blog post (admin only)."""
    return await service.update_post(post_id, data)


@router.delete("/posts/{post_id}")
async def delete_post(
    post_id: UUID,
    current_user: User = Depends(require_role("admin")),
    service: BlogService = Depends(get_blog_service),
):
    """Delete blog post (admin only)."""
    success = await service.delete_post(post_id)
    if not success:
        raise HTTPException(status_code=404, detail="Post not found")
    return {"message": "Post deleted"}


@router.get("/comments/pending", response_model=List[CommentAdminRead])
async def list_pending_comments(
    current_user: User = Depends(require_role("admin")),
    service: BlogService = Depends(get_blog_service),
):
    """List all comments awaiting approval (admin only)."""
    return await service.get_pending_comments()


@router.put("/comments/{comment_id}/approve", response_model=CommentAdminRead)
async def approve_comment(
    comment_id: UUID,
    current_user: User = Depends(require_role("admin")),
    service: BlogService = Depends(get_blog_service),
):
    """Approve a comment (admin only)."""
    return await service.approve_comment(comment_id)


@router.delete("/comments/{comment_id}")
async def delete_comment(
    comment_id: UUID,
    current_user: User = Depends(require_role("admin")),
    service: BlogService = Depends(get_blog_service),
):
    """Delete a comment (admin only)."""
    success = await service.delete_comment(comment_id)
    if not success:
        raise HTTPException(status_code=404, detail="Comment not found")
    return {"message": "Comment deleted"}
