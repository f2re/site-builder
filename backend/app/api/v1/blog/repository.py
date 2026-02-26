# Module: api/v1/blog/repository.py | Agent: backend-agent | Task: phase3_backend_blog
from typing import List, Optional, Tuple
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from app.db.models.blog import BlogPost, BlogCategory, Tag, BlogStatus
from app.db.session import get_db

class BlogRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_slug(self, slug: str, status: Optional[BlogStatus] = None) -> Optional[BlogPost]:
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
        status: BlogStatus = BlogStatus.published,
        is_featured: Optional[bool] = None,
        cursor: Optional[UUID] = None,
        per_page: int = 20,
    ) -> Tuple[List[BlogPost], Optional[str], int]:
        
        # Base count query
        count_stmt = select(func.count(BlogPost.id)).where(BlogPost.status == status)
        
        # Base list query
        stmt = (
            select(BlogPost)
            .where(BlogPost.status == status)
            .options(
                selectinload(BlogPost.category),
                selectinload(BlogPost.tags),
                selectinload(BlogPost.author)
            )
        )
        
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

    async def get_categories(self) -> List[BlogCategory]:
        stmt = select(BlogCategory).order_by(BlogCategory.name)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

async def get_blog_repo(session: AsyncSession = Depends(get_db)) -> BlogRepository:
    return BlogRepository(session)
