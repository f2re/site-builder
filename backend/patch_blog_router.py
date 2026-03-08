import re

with open("backend/app/api/v1/blog/router.py", "r") as f:
    content = f.read()

# Replace the list_posts signature and body
old_list_posts = '''@router.get("/posts", response_model=BlogPagination)
async def list_posts(
    status: Optional[BlogPostStatus] = Query(None, description="Filter by status: DRAFT|PUBLISHED|ARCHIVED. Default is PUBLISHED for guests, all for admins."),
    category: Optional[str] = Query(None, description="Filter by category slug"),
    tag: Optional[str] = Query(None, description="Filter by tag slug"),
    after: Optional[str] = Query(None, description="Cursor for pagination (base64-encoded composite cursor)"),
    limit: int = Query(12, ge=1, le=100),
    current_user: Optional[User] = Depends(get_optional_current_user),
    service: BlogService = Depends(get_blog_service),
):
    """List blog posts with pagination and filters."""
    # Logic: if status is not provided:
    # - admins see all
    # - guests see only PUBLISHED
    effective_status = status
    is_admin = current_user and current_user.role == "admin"

    if effective_status is None and not is_admin:
        effective_status = BlogPostStatus.PUBLISHED

    return await service.list_posts(
        status=effective_status,
        category_slug=category,
        tag_slug=tag,
        cursor=after,
        per_page=limit,
    )'''

new_list_posts = '''@router.get("/posts", response_model=BlogPagination)
async def list_posts(
    status: Optional[str] = Query(None, description="Filter by status: DRAFT|PUBLISHED|ARCHIVED|all. Default is PUBLISHED for guests, all for admins."),
    category: Optional[str] = Query(None, description="Filter by category slug"),
    tag: Optional[str] = Query(None, description="Filter by tag slug"),
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

    actual_limit = limit if limit is not None else per_page

    return await service.list_posts(
        status=effective_status,
        category_slug=category,
        tag_slug=tag,
        cursor=after,
        per_page=actual_limit,
    )'''

content = content.replace(old_list_posts, new_list_posts)

# Also fix list_posts_admin just in case it receives "all"
old_list_posts_admin = '''@router.get("/posts/admin", response_model=BlogPagination)
async def list_posts_admin(
    status: Optional[BlogPostStatus] = Query(None),
    category: Optional[str] = Query(None),
    tag: Optional[str] = Query(None),
    after: Optional[str] = Query(None, description="Cursor for pagination (base64-encoded composite cursor)"),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(require_admin),
    service: BlogService = Depends(get_blog_service),
):
    """Admin-specific list of posts (defaults to all statuses)."""
    return await service.list_posts(
        status=status,
        category_slug=category,
        tag_slug=tag,
        cursor=after,
        per_page=limit,
    )'''

new_list_posts_admin = '''@router.get("/posts/admin", response_model=BlogPagination)
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

    actual_limit = limit if limit is not None else per_page

    return await service.list_posts(
        status=effective_status,
        category_slug=category,
        tag_slug=tag,
        cursor=after,
        per_page=actual_limit,
    )'''

content = content.replace(old_list_posts_admin, new_list_posts_admin)

with open("backend/app/api/v1/blog/router.py", "w") as f:
    f.write(content)
