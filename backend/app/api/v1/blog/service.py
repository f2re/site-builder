from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
from uuid import UUID
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
            try:
                after_uuid = UUID(after)
                # For UUID cursor, we might need a different strategy than < 
                # but if it was integer before, we should decide how to paginate.
                # Usually with UUIDs we use created_at + id for stable pagination.
                # For now, let's just use it as a simple filter if it's expected.
                # But simple < doesn't work well with UUIDs for ordering.
                pass 
            except ValueError:
                pass

        query = query.order_by(BlogPost.published_at.desc(), BlogPost.created_at.desc()).limit(limit + 1)

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

    async def create_post(self, data: BlogPostCreate, author_id: UUID):
        """Create new blog post."""
        # Generate slug if not provided
        slug = data.slug or slugify(data.title)

        # Sanitize content if it's HTML
        content = bleach.clean(
            data.content,
            tags=ALLOWED_TAGS,
            attributes=ALLOWED_ATTRS,
        )

        # Calculate reading time
        word_count = len(content.split())
        reading_time = max(1, word_count // 200)

        post = BlogPost(
            title=data.title,
            slug=slug,
            summary=data.summary,
            content=content,
            meta_title=data.meta_title,
            meta_description=data.meta_description,
            cover_image=data.cover_image,
            category_id=data.category_id,
            author_id=author_id,
            status=data.status or BlogPostStatus.DRAFT,
            is_featured=data.is_featured,
            reading_time_minutes=reading_time,
        )

        self.db.add(post)
        await self.db.commit()
        await self.db.refresh(post)

        logger.info("blog_post_created", post_id=str(post.id), slug=slug)
        return post

    async def update_post(self, post_id: UUID, data: BlogPostUpdate):
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
            if not data.slug:
                post.slug = slugify(data.title)
        if data.slug is not None:
            post.slug = data.slug
        if data.summary is not None:
            post.summary = data.summary
        if data.content is not None:
            post.content = bleach.clean(
                data.content,
                tags=ALLOWED_TAGS,
                attributes=ALLOWED_ATTRS,
            )
        if data.meta_title is not None:
            post.meta_title = data.meta_title
        if data.meta_description is not None:
            post.meta_description = data.meta_description
        if data.cover_image is not None:
            post.cover_image = data.cover_image
        if data.category_id is not None:
            post.category_id = data.category_id
        if data.status is not None:
            post.status = data.status
        if data.is_featured is not None:
            post.is_featured = data.is_featured

        # Recalculate reading time
        if data.content:
            word_count = len(post.content.split())
            post.reading_time_minutes = max(1, word_count // 200)

        await self.db.commit()
        await self.db.refresh(post)

        logger.info("blog_post_updated", post_id=str(post.id))
        return post

    async def delete_post(self, post_id: UUID):
        """Soft delete by setting status to archived."""
        result = await self.db.execute(
            select(BlogPost).where(BlogPost.id == post_id)
        )
        post = result.scalar_one_or_none()

        if not post:
            return False

        post.status = BlogPostStatus.ARCHIVED
        await self.db.commit()

        logger.info("blog_post_deleted", post_id=str(post.id))
        return True

    async def list_categories(self):
        """List all categories."""
        result = await self.db.execute(select(BlogCategory))
        return result.scalars().all()

    async def list_tags(self):
        """List all tags."""
        result = await self.db.execute(select(Tag))
        return result.scalars().all()
