from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List
import structlog
import bleach
from slugify import slugify

from app.db.models.blog import BlogPost, BlogCategory, Tag, BlogPostStatus
from .schemas import BlogPostCreate, BlogPostUpdate

logger = structlog.get_logger()

# HTML sanitization config
ALLOWED_TAGS = bleach.sanitizer.ALLOWED_TAGS | {
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'p', 'br', 'ul', 'ol', 'li',
    'strong', 'em', 'b', 'i', 'u',
    'blockquote', 'code', 'pre',
    'img', 'figure', 'figcaption',
    'a', 'table', 'thead', 'tbody', 'tr', 'th', 'td',
}
ALLOWED_ATTRS = {
    'a': ['href', 'title', 'rel', 'target'],
    'img': ['src', 'alt', 'width', 'height', 'loading', 'class'],
    '*': ['class'],
}


class BlogService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_posts(
        self,
        status: str | None = None,
        category: str | None = None,
        tag: str | None = None,
        after: str | None = None,
        limit: int = 12,
    ):
        """List posts with filters and cursor pagination."""
        query = select(BlogPost)

        # Filters
        if status:
            query = query.where(BlogPost.status == status)
        if category:
            query = query.join(BlogCategory).where(BlogCategory.slug == category)
        if tag:
            query = query.join(BlogPost.tags).where(Tag.slug == tag)

        # Cursor pagination
        if after:
            query = query.where(BlogPost.id < int(after))

        query = query.order_by(BlogPost.published_at.desc()).limit(limit + 1)

        result = await self.db.execute(query)
        posts = result.scalars().all()

        has_more = len(posts) > limit
        posts = posts[:limit]

        return {
            "items": posts,
            "pageInfo": {
                "hasMore": has_more,
                "endCursor": str(posts[-1].id) if posts else None,
            }
        }

    async def get_post_by_slug(self, slug: str):
        """Get post by slug and increment views."""
        result = await self.db.execute(
            select(BlogPost).where(BlogPost.slug == slug)
        )
        post = result.scalar_one_or_none()

        if post:
            # Increment views (async, non-blocking)
            post.views += 1
            await self.db.commit()

        return post

    async def create_post(self, data: BlogPostCreate, author_id: int):
        """Create new blog post."""
        # Generate slug
        slug = slugify(data.title)

        # Sanitize HTML
        content_html = bleach.clean(
            data.content_html,
            tags=ALLOWED_TAGS,
            attributes=ALLOWED_ATTRS,
        )

        # Calculate reading time
        word_count = len(content_html.split())
        reading_time = max(1, word_count // 200)

        post = BlogPost(
            title=data.title,
            slug=slug,
            excerpt=data.excerpt,
            content_json=data.content_json,
            content_html=content_html,
            meta_title=data.meta_title,
            meta_description=data.meta_description,
            og_image_url=data.og_image_url,
            category_id=data.category_id,
            author_id=author_id,
            status=data.status or BlogPostStatus.DRAFT,
            reading_time_minutes=reading_time,
        )

        self.db.add(post)
        await self.db.commit()
        await self.db.refresh(post)

        logger.info("blog_post_created", post_id=post.id, slug=slug)
        return post

    async def update_post(self, post_id: int, data: BlogPostUpdate):
        """Update blog post."""
        result = await self.db.execute(
            select(BlogPost).where(BlogPost.id == post_id)
        )
        post = result.scalar_one_or_none()

        if not post:
            return None

        # Update fields
        if data.title is not None:
            post.title = data.title
            post.slug = slugify(data.title)
        if data.excerpt is not None:
            post.excerpt = data.excerpt
        if data.content_html is not None:
            post.content_html = bleach.clean(
                data.content_html,
                tags=ALLOWED_TAGS,
                attributes=ALLOWED_ATTRS,
            )
        if data.content_json is not None:
            post.content_json = data.content_json
        if data.meta_title is not None:
            post.meta_title = data.meta_title
        if data.meta_description is not None:
            post.meta_description = data.meta_description
        if data.og_image_url is not None:
            post.og_image_url = data.og_image_url
        if data.category_id is not None:
            post.category_id = data.category_id
        if data.status is not None:
            post.status = data.status

        # Recalculate reading time
        if data.content_html:
            word_count = len(post.content_html.split())
            post.reading_time_minutes = max(1, word_count // 200)

        await self.db.commit()
        await self.db.refresh(post)

        logger.info("blog_post_updated", post_id=post.id)
        return post

    async def delete_post(self, post_id: int):
        """Soft delete by setting status to archived."""
        result = await self.db.execute(
            select(BlogPost).where(BlogPost.id == post_id)
        )
        post = result.scalar_one_or_none()

        if not post:
            return False

        post.status = BlogPostStatus.ARCHIVED
        await self.db.commit()

        logger.info("blog_post_deleted", post_id=post.id)
        return True

    async def list_categories(self):
        """List all categories."""
        result = await self.db.execute(select(BlogCategory))
        return result.scalars().all()

    async def list_tags(self):
        """List all tags."""
        result = await self.db.execute(select(Tag))
        return result.scalars().all()
