# Module: api/v1/blog/router.py | Agent: backend-agent | Task: p28_backend_blog_categories
from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import List, Optional, Union
from uuid import UUID

from app.core.dependencies import get_optional_current_user, require_admin
from app.db.models.user import User
from app.db.models.blog import BlogPostStatus
from .schemas import (
    BlogCategoryCreate,
    BlogCategoryRead,
    BlogCategoryUpdate,
    BlogPagination,
    BlogPostRead,
    BlogPostCreate,
    BlogPostUpdate,
    CommentCreate,
    CommentRead,
    CommentAdminRead,
    TagRead,
)
from .service import BlogService, get_blog_service

router = APIRouter(prefix="/blog", tags=["Blog"])


@router.get("/posts", response_model=BlogPagination)
async def list_posts(
    status: Optional[str] = Query(None, description="Filter by status: DRAFT|PUBLISHED|ARCHIVED|all. Default is PUBLISHED for guests, all for admins."),
    category: Optional[str] = Query(None, description="Filter by category slug"),
    tag: Optional[str] = Query(None, description="Filter by tag slug"),
    section: Optional[str] = Query(None, description="Filter by category section: news|instructions"),
    after: Optional[str] = Query(None, description="Cursor for pagination (base64-encoded composite cursor)"),
    limit: Optional[int] = Query(None, ge=1, le=100),
    per_page: Optional[int] = Query(12, ge=1, le=100),
    current_user: Optional[User] = Depends(get_optional_current_user),
    service: BlogService = Depends(get_blog_service),
):
    """List blog posts with pagination and filters."""
    effective_status = status
    is_admin = current_user is not None and current_user.role == "admin"

    if effective_status == "all" or effective_status == "":
        effective_status = None

    if effective_status is None and not is_admin:
        effective_status = BlogPostStatus.PUBLISHED
    elif effective_status is not None:
        try:
            effective_status = BlogPostStatus(effective_status)
        except ValueError:
            raise HTTPException(status_code=422, detail=f"Invalid status: {effective_status}")

    actual_limit = limit if limit is not None else (per_page if per_page is not None else 20)

    return await service.list_posts(
        status=effective_status,
        category_slug=category,
        tag_slug=tag,
        section=section,
        cursor=after,
        per_page=actual_limit,
    )


@router.get("/posts/{slug}", response_model=BlogPostRead)
async def get_post(
    slug: str,
    current_user: Optional[User] = Depends(get_optional_current_user),
    service: BlogService = Depends(get_blog_service),
):
    """Get single blog post by slug."""
    is_admin = current_user is not None and current_user.role == "admin"
    return await service.get_post_detail(slug, is_admin=is_admin)


@router.get("/categories", response_model=List[BlogCategoryRead])
async def list_categories(
    section: Optional[str] = Query(None, description="Filter by section: news|instructions"),
    service: BlogService = Depends(get_blog_service),
):
    """List all blog categories with post counts."""
    return await service.list_categories(section=section)


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
    current_user: Optional[User] = Depends(get_optional_current_user),
    service: BlogService = Depends(get_blog_service),
):
    """List approved comments for a post (Admins see all and decrypted emails)."""
    is_admin = current_user.role == "admin" if current_user else False
    return await service.get_comments(post_id, is_admin=is_admin)


# Admin endpoints
@router.post("/posts", response_model=BlogPostRead, status_code=status.HTTP_201_CREATED)
async def create_post(
    data: BlogPostCreate,
    current_user: User = Depends(require_admin),
    service: BlogService = Depends(get_blog_service),
):
    """Create new blog post (admin only)."""
    return await service.create_post(data, user_id=current_user.id)


@router.get("/posts/admin", response_model=BlogPagination)
async def list_posts_admin(
    status: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    tag: Optional[str] = Query(None),
    after: Optional[str] = Query(None, description="Cursor for pagination (base64-encoded composite cursor)"),
    limit: Optional[int] = Query(None, ge=1, le=100),
    per_page: Optional[int] = Query(20, ge=1, le=100),
    current_user: User = Depends(require_admin),
    service: BlogService = Depends(get_blog_service),
):
    """Admin-specific list of posts (defaults to all statuses)."""
    effective_status = status
    if effective_status == "all" or effective_status == "":
        effective_status = None
    elif effective_status is not None:
        try:
            effective_status = BlogPostStatus(effective_status)
        except ValueError:
            raise HTTPException(status_code=422, detail=f"Invalid status: {effective_status}")

    actual_limit = limit if limit is not None else (per_page if per_page is not None else 20)

    return await service.list_posts(
        status=effective_status,
        category_slug=category,
        tag_slug=tag,
        cursor=after,
        per_page=actual_limit,
    )


# Admin Blog Category CRUD
@router.get("/admin/categories", response_model=List[BlogCategoryRead])
async def admin_list_categories(
    section: Optional[str] = Query(None, description="Filter by section: news|instructions"),
    current_user: User = Depends(require_admin),
    service: BlogService = Depends(get_blog_service),
):
    """List all blog categories (admin)."""
    return await service.list_categories(section=section)


@router.post("/admin/categories", response_model=BlogCategoryRead, status_code=status.HTTP_201_CREATED)
async def admin_create_category(
    data: BlogCategoryCreate,
    current_user: User = Depends(require_admin),
    service: BlogService = Depends(get_blog_service),
):
    """Create a new blog category (admin)."""
    return await service.create_category(data)


@router.put("/admin/categories/{category_id}", response_model=BlogCategoryRead)
async def admin_update_category(
    category_id: UUID,
    data: BlogCategoryUpdate,
    current_user: User = Depends(require_admin),
    service: BlogService = Depends(get_blog_service),
):
    """Update a blog category (admin)."""
    return await service.update_category(category_id, data)


@router.delete("/admin/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def admin_delete_category(
    category_id: UUID,
    current_user: User = Depends(require_admin),
    service: BlogService = Depends(get_blog_service),
):
    """Delete a blog category (admin)."""
    success = await service.delete_category(category_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")


@router.put("/posts/{post_id}", response_model=BlogPostRead)
async def update_post(
    post_id: UUID,
    data: BlogPostUpdate,
    current_user: User = Depends(require_admin),
    service: BlogService = Depends(get_blog_service),
):
    """Update blog post (admin only)."""
    return await service.update_post(post_id, data)


@router.delete("/posts/{post_id}")
async def delete_post(
    post_id: UUID,
    current_user: User = Depends(require_admin),
    service: BlogService = Depends(get_blog_service),
):
    """Delete blog post (admin only)."""
    success = await service.delete_post(post_id)
    if not success:
        raise HTTPException(status_code=404, detail="Post not found")
    return {"message": "Post deleted"}


@router.get("/comments/pending", response_model=List[CommentAdminRead])
async def list_pending_comments(
    current_user: User = Depends(require_admin),
    service: BlogService = Depends(get_blog_service),
):
    """List all comments awaiting approval (admin only)."""
    return await service.get_pending_comments()


@router.put("/comments/{comment_id}/approve", response_model=CommentAdminRead)
async def approve_comment(
    comment_id: UUID,
    current_user: User = Depends(require_admin),
    service: BlogService = Depends(get_blog_service),
):
    """Approve a comment (admin only)."""
    return await service.approve_comment(comment_id)


@router.delete("/comments/{comment_id}")
async def delete_comment(
    comment_id: UUID,
    current_user: User = Depends(require_admin),
    service: BlogService = Depends(get_blog_service),
):
    """Delete a comment (admin only)."""
    success = await service.delete_comment(comment_id)
    if not success:
        raise HTTPException(status_code=404, detail="Comment not found")
    return {"message": "Comment deleted"}
