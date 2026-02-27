# Module: api/v1/blog/repository.py | Agent: backend-agent | Task: BE-02
from typing import List, Optional, Tuple
from uuid import UUID

from sqlalchemy import select, func, update, delete
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from app.db.models.blog import BlogPost, BlogCategory, Tag, BlogPostStatus, Author, Comment, CommentStatus
from app.db.session import get_db

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
        cursor: Optional[UUID] = None,
        per_page: int = 20,
    ) -> Tuple[List[BlogPost], Optional[str], int]:
        
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

        # Cursor pagination
        if cursor:
            stmt = stmt.where(BlogPost.id > cursor)
            
        stmt = stmt.order_by(BlogPost.id).limit(per_page + 1)
        
        result = await self.session.execute(stmt)
        posts = list(result.scalars().all())
        
        items = posts[:per_page]
        next_cursor = None
        if len(posts) > per_page:
            next_cursor = str(items[-1].id)
            
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
        return result.rowcount > 0

    async def get_categories(self) -> List[BlogCategory]:
        stmt = select(BlogCategory).order_by(BlogCategory.name)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_all_tags(self) -> List[Tag]:
        stmt = select(Tag).order_by(Tag.name)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

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
        return result.rowcount > 0

    async def get_pending_comments(self) -> List[Comment]:
        stmt = select(Comment).where(Comment.status == CommentStatus.PENDING).order_by(Comment.created_at.desc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

async def get_blog_repo(session: AsyncSession = Depends(get_db)) -> BlogRepository:
    return BlogRepository(session)
