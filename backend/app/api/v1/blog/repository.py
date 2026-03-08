# Module: api/v1/blog/repository.py | Agent: backend-agent | Task: p28_backend_blog_categories
import base64
import json
from datetime import datetime
from typing import List, Optional, Tuple
from uuid import UUID

from sqlalchemy import select, func, update, delete, tuple_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from app.db.models.blog import BlogPost, BlogCategory, Tag, BlogPostStatus, Author, Comment, CommentStatus
from app.db.session import get_db


def _encode_cursor(published_at: Optional[datetime], post_id: UUID) -> str:
    """Encode (published_at, id) pair as base64 JSON cursor."""
    ts = published_at.isoformat() if published_at else ""
    payload = json.dumps({"published_at": ts, "id": str(post_id)})
    return base64.urlsafe_b64encode(payload.encode()).decode()


def _decode_cursor(cursor: str) -> Optional[Tuple[Optional[datetime], UUID]]:
    """Decode base64 JSON cursor into (published_at, id) pair. Returns None if invalid."""
    try:
        payload = json.loads(base64.urlsafe_b64decode(cursor.encode()).decode())
        ts_str = payload.get("published_at", "")
        published_at: Optional[datetime] = datetime.fromisoformat(ts_str) if ts_str else None
        post_id = UUID(payload["id"])
        return published_at, post_id
    except Exception:
        return None


class BlogRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, post_id: UUID) -> Optional[BlogPost]:
        stmt = (
            select(BlogPost)
            .where(BlogPost.id == post_id)
            .options(
                selectinload(BlogPost.category),
                selectinload(BlogPost.tags),
                selectinload(BlogPost.author)
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_slug(self, slug: str, status: Optional[BlogPostStatus] = None) -> Optional[BlogPost]:
        stmt = (
            select(BlogPost)
            .where(BlogPost.slug == slug)
            .options(
                selectinload(BlogPost.category),
                selectinload(BlogPost.tags),
                selectinload(BlogPost.author)
            )
        )
        if status:
            stmt = stmt.where(BlogPost.status == status)

        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_posts(
        self,
        category_slug: Optional[str] = None,
        tag_slug: Optional[str] = None,
        status: Optional[BlogPostStatus] = BlogPostStatus.PUBLISHED,
        is_featured: Optional[bool] = None,
        cursor: Optional[str] = None,
        per_page: int = 20,
    ) -> Tuple[List[BlogPost], Optional[str], int]:
        """
        List blog posts with composite cursor pagination by (published_at DESC, id DESC).
        Cursor is a base64-encoded JSON string: {published_at: ISO, id: UUID}.
        """
        # Base count query
        count_stmt = select(func.count(BlogPost.id))
        if status:
            count_stmt = count_stmt.where(BlogPost.status == status)

        # Base list query
        stmt = (
            select(BlogPost)
            .options(
                selectinload(BlogPost.category),
                selectinload(BlogPost.tags),
                selectinload(BlogPost.author)
            )
        )
        if status:
            stmt = stmt.where(BlogPost.status == status)

        if is_featured is not None:
            count_stmt = count_stmt.where(BlogPost.is_featured == is_featured)
            stmt = stmt.where(BlogPost.is_featured == is_featured)

        if category_slug:
            stmt = stmt.join(BlogCategory).where(BlogCategory.slug == category_slug)
            count_stmt = count_stmt.join(BlogCategory).where(BlogCategory.slug == category_slug)

        if tag_slug:
            stmt = stmt.join(BlogPost.tags).where(Tag.slug == tag_slug)
            count_stmt = count_stmt.join(BlogPost.tags).where(Tag.slug == tag_slug)

        # Get total count
        count_result = await self.session.execute(count_stmt)
        total = count_result.scalar_one()

        # Composite cursor pagination: ORDER BY published_at DESC, id DESC
        # Cursor encodes the last seen (published_at, id) pair.
        # WHERE (published_at, id) < (cursor_published_at, cursor_id) using tuple comparison.
        if cursor:
            decoded = _decode_cursor(cursor)
            if decoded is not None:
                cursor_published_at, cursor_id = decoded
                stmt = stmt.where(
                    tuple_(BlogPost.published_at, BlogPost.id)
                    < tuple_(cursor_published_at, cursor_id)
                )

        stmt = stmt.order_by(BlogPost.published_at.desc(), BlogPost.id.desc()).limit(per_page + 1)

        result = await self.session.execute(stmt)
        posts = list(result.scalars().all())

        items = posts[:per_page]
        next_cursor: Optional[str] = None
        if len(posts) > per_page:
            last = items[-1]
            next_cursor = _encode_cursor(last.published_at, last.id)

        return items, next_cursor, total

    async def create(self, post: BlogPost) -> BlogPost:
        self.session.add(post)
        await self.session.flush()
        await self.session.refresh(post)
        return post

    async def update(self, post_id: UUID, **kwargs) -> Optional[BlogPost]:
        stmt = (
            update(BlogPost)
            .where(BlogPost.id == post_id)
            .values(**kwargs)
            .returning(BlogPost)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def delete(self, post_id: UUID) -> bool:
        stmt = delete(BlogPost).where(BlogPost.id == post_id)
        result = await self.session.execute(stmt)
        return getattr(result, "rowcount", 0) > 0

    async def get_categories(self) -> List[BlogCategory]:
        stmt = select(BlogCategory).order_by(BlogCategory.name)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_categories_with_count(self) -> List[Tuple[BlogCategory, int]]:
        """Return categories with count of published posts in each."""
        stmt = (
            select(BlogCategory, func.count(BlogPost.id).label("posts_count"))
            .outerjoin(BlogPost, (BlogPost.category_id == BlogCategory.id) & (BlogPost.status == BlogPostStatus.PUBLISHED))
            .group_by(BlogCategory.id)
            .order_by(BlogCategory.name)
        )
        result = await self.session.execute(stmt)
        return [(row[0], row[1]) for row in result.all()]

    async def get_category_by_id(self, category_id: UUID) -> Optional[BlogCategory]:
        stmt = select(BlogCategory).where(BlogCategory.id == category_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_category_by_slug(self, slug: str) -> Optional[BlogCategory]:
        stmt = select(BlogCategory).where(BlogCategory.slug == slug)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_category(self, category: BlogCategory) -> BlogCategory:
        self.session.add(category)
        await self.session.flush()
        await self.session.refresh(category)
        return category

    async def update_category(self, category_id: UUID, **kwargs) -> Optional[BlogCategory]:
        stmt = (
            update(BlogCategory)
            .where(BlogCategory.id == category_id)
            .values(**kwargs)
            .returning(BlogCategory)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def delete_category(self, category_id: UUID) -> bool:
        stmt = delete(BlogCategory).where(BlogCategory.id == category_id)
        result = await self.session.execute(stmt)
        return getattr(result, "rowcount", 0) > 0

    async def get_all_tags(self) -> List[Tag]:
        stmt = select(Tag).order_by(Tag.name)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_tag_by_name(self, name: str) -> Optional[Tag]:
        stmt = select(Tag).where(Tag.name == name)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_tag(self, tag: Tag) -> Tag:
        self.session.add(tag)
        await self.session.flush()
        await self.session.refresh(tag)
        return tag

    async def get_author_by_user_id(self, user_id: UUID) -> Optional[Author]:
        stmt = select(Author).where(Author.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_author(self, author: Author) -> Author:
        self.session.add(author)
        await self.session.flush()
        await self.session.refresh(author)
        return author

    async def create_comment(self, comment: Comment) -> Comment:
        self.session.add(comment)
        await self.session.flush()
        await self.session.refresh(comment)
        return comment

    async def get_comments_by_post_id(self, post_id: UUID, status: Optional[CommentStatus] = None) -> List[Comment]:
        stmt = select(Comment).where(Comment.post_id == post_id)
        if status:
            stmt = stmt.where(Comment.status == status)
        stmt = stmt.order_by(Comment.created_at.desc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_comment_by_id(self, comment_id: UUID) -> Optional[Comment]:
        stmt = select(Comment).where(Comment.id == comment_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def update_comment_status(self, comment_id: UUID, status: CommentStatus) -> Optional[Comment]:
        stmt = (
            update(Comment)
            .where(Comment.id == comment_id)
            .values(status=status)
            .returning(Comment)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def delete_comment(self, comment_id: UUID) -> bool:
        stmt = delete(Comment).where(Comment.id == comment_id)
        result = await self.session.execute(stmt)
        return getattr(result, "rowcount", 0) > 0

    async def get_pending_comments(self) -> List[Comment]:
        stmt = select(Comment).where(Comment.status == CommentStatus.PENDING).order_by(Comment.created_at.desc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())


async def get_blog_repo(session: AsyncSession = Depends(get_db)) -> BlogRepository:
    return BlogRepository(session)
