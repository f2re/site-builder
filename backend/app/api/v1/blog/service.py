import bleach
from uuid import UUID
from typing import List, Optional, Tuple
from fastapi import Depends, HTTPException, status

from app.api.v1.blog.repository import BlogRepository, get_blog_repo
from app.api.v1.blog.schemas import BlogPostCreate, BlogPostUpdate, BlogPostRead
from app.db.models.blog import BlogPost, BlogStatus
from app.tasks.search import index_blog_post_task, remove_blog_post_from_index_task

ALLOWED_TAGS = bleach.sanitizer.ALLOWED_TAGS | {
    'h1','h2','h3','h4','p','br','ul','ol','li',
    'strong','em','blockquote','code','pre',
    'img','figure','figcaption','a','table','thead','tbody','tr','th','td',
    'iframe',
}
ALLOWED_ATTRS = {
    'a': ['href', 'title', 'rel', 'target'],
    'img': ['src', 'alt', 'width', 'height', 'loading'],
    'iframe': ['src', 'width', 'height', 'allowfullscreen'],
}

class BlogService:
    def __init__(self, repo: BlogRepository = Depends(get_blog_repo)):
        self.repo = repo

    def _sanitize_html(self, html: str) -> str:
        return bleach.clean(html, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRS)

    async def create_post(self, author_id: UUID, data: BlogPostCreate) -> BlogPost:
        content_html = self._sanitize_html(data.content) # Assuming 'content' is HTML from TipTap
        
        post = BlogPost(
            author_id=author_id,
            title=data.title,
            slug=data.slug,
            content=content_html,
            summary=data.summary,
            status=data.status,
            category_id=data.category_id,
            meta_title=data.meta_title,
            meta_description=data.meta_description,
            reading_time_minutes=max(1, len(content_html.split()) // 200)
        )
        
        created_post = await self.repo.create(post)
        
        # Index in Meilisearch if published
        if created_post.status == BlogStatus.published:
            index_blog_post_task.delay({
                "id": str(created_post.id),
                "title": created_post.title,
                "summary": created_post.summary,
                "content": created_post.content,
                "slug": created_post.slug
            })
            
        return created_post

    async def update_post(self, post_id: UUID, data: BlogPostUpdate) -> BlogPost:
        update_data = data.model_dump(exclude_unset=True)
        
        if "content" in update_data:
            update_data["content"] = self._sanitize_html(update_data["content"])
            update_data["reading_time_minutes"] = max(1, len(update_data["content"].split()) // 200)
            
        updated_post = await self.repo.update(post_id, **update_data)
        if not updated_post:
            raise HTTPException(status_code=404, detail="Post not found")
            
        # Update Meilisearch
        if updated_post.status == BlogStatus.published:
            index_blog_post_task.delay({
                "id": str(updated_post.id),
                "title": updated_post.title,
                "summary": updated_post.summary,
                "content": updated_post.content,
                "slug": updated_post.slug
            })
        else:
            remove_blog_post_from_index_task.delay(str(updated_post.id))
            
        return updated_post

    async def delete_post(self, post_id: UUID) -> bool:
        success = await self.repo.delete(post_id)
        if success:
            remove_blog_post_from_index_task.delay(str(post_id))
        return success

async def get_blog_service(repo: BlogRepository = Depends(get_blog_repo)) -> BlogService:
    return BlogService(repo)
