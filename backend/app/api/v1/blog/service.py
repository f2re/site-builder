# Module: api/v1/blog/service.py | Agent: backend-agent | Task: phase11_backend_admin_blog_refinement
import bleach
from typing import List, Optional, Any
from uuid import UUID
from fastapi import Depends, HTTPException, status
import structlog
from slugify import slugify

from app.api.v1.blog.repository import BlogRepository, get_blog_repo
from app.api.v1.blog.schemas import (
    BlogPostCreate,
    BlogPostUpdate,
    BlogPagination,
    BlogPostRead
)
from app.db.models.blog import BlogPost, BlogPostStatus
from app.tasks.search import index_blog_post_task, remove_blog_post_from_index_task

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

def tiptap_to_text(json_content: Any) -> str:
    """Extract plain text from TipTap JSON for word counting."""
    if not json_content or not isinstance(json_content, dict):
        return ""
    
    text_parts = []
    
    def walk(node: Any):
        if not isinstance(node, dict):
            return
        if node.get("type") == "text":
            text_parts.append(node.get("text", ""))
        
        for child in node.get("content", []):
            walk(child)
            
    walk(json_content)
    return " ".join(text_parts)

def tiptap_to_html(json_content: Any) -> str:
    """Very basic TipTap JSON to HTML converter."""
    if not json_content or not isinstance(json_content, dict):
        return ""
    
    def render_node(node: Any) -> str:
        if not isinstance(node, dict):
            return ""
        
        node_type = node.get("type")
        content = "".join(render_node(child) for child in node.get("content", []))
        
        if node_type == "doc":
            return content
        elif node_type == "paragraph":
            return f"<p>{content}</p>"
        elif node_type == "text":
            text = node.get("text", "")
            # Apply marks
            for mark in node.get("marks", []):
                mark_type = mark.get("type")
                if mark_type == "bold":
                    text = f"<strong>{text}</strong>"
                elif mark_type == "italic":
                    text = f"<em>{text}</em>"
                elif mark_type == "strike":
                    text = f"<s>{text}</s>"
                elif mark_type == "link":
                    href = mark.get("attrs", {}).get("href", "#")
                    text = f'<a href="{href}">{text}</a>'
            return text
        elif node_type == "heading":
            level = node.get("attrs", {}).get("level", 1)
            return f"<h{level}>{content}</h{level}>"
        elif node_type == "bulletList":
            return f"<ul>{content}</ul>"
        elif node_type == "orderedList":
            return f"<ol>{content}</ol>"
        elif node_type == "listItem":
            return f"<li>{content}</li>"
        elif node_type == "blockquote":
            return f"<blockquote>{content}</blockquote>"
        elif node_type == "image":
            src = node.get("attrs", {}).get("src", "")
            alt = node.get("attrs", {}).get("alt", "")
            return f'<img src="{src}" alt="{alt}" />'
        elif node_type == "hardBreak":
            return "<br />"
        elif node_type == "horizontalRule":
            return "<hr />"
        elif node_type == "codeBlock":
            return f"<pre><code>{content}</code></pre>"
        
        return content

    return render_node(json_content)

class BlogService:
    def __init__(self, repo: BlogRepository = Depends(get_blog_repo)):
        self.repo = repo

    async def list_posts(
        self,
        category_slug: Optional[str] = None,
        tag_slug: Optional[str] = None,
        status: Optional[BlogPostStatus] = BlogPostStatus.PUBLISHED,
        is_featured: Optional[bool] = None,
        cursor: Optional[UUID] = None,
        per_page: int = 20,
    ) -> BlogPagination:
        items, next_cursor, total = await self.repo.list_posts(
            category_slug=category_slug,
            tag_slug=tag_slug,
            status=status,
            is_featured=is_featured,
            cursor=cursor,
            per_page=per_page
        )
        return BlogPagination(
            items=items,
            pageInfo={
                "nextCursor": next_cursor,
                "total": total,
                "hasMore": next_cursor is not None
            }
        )

    async def get_post_detail(self, slug: str) -> BlogPostRead:
        post = await self.repo.get_by_slug(slug)
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Blog post not found"
            )
        # In a real app, we might want to increment views here
        # post.views += 1
        # await self.repo.session.commit()
        return BlogPostRead.model_validate(post)

    async def create_post(self, data: BlogPostCreate, author_id: UUID) -> BlogPostRead:
        """
        Create a new blog post, generate HTML from JSON, calculate reading time, and index in search.
        """
        slug = data.slug or slugify(data.title)
        
        # Generate HTML from JSON
        content_html = tiptap_to_html(data.content_json)
        # Sanitize HTML
        content_html = bleach.clean(
            content_html,
            tags=ALLOWED_TAGS,
            attributes=ALLOWED_ATTRS,
        )
        
        # Calculate reading time
        plain_text = tiptap_to_text(data.content_json)
        word_count = len(plain_text.split())
        reading_time = max(1, word_count // 200)
        
        post = BlogPost(
            title=data.title,
            slug=slug,
            summary=data.summary,
            content_json=data.content_json,
            content_html=content_html,
            status=data.status,
            is_featured=data.is_featured,
            category_id=data.category_id,
            author_id=author_id,
            cover_image=data.cover_image,
            meta_title=data.meta_title,
            meta_description=data.meta_description,
            reading_time_minutes=reading_time
        )
        
        created_post = await self.repo.create(post)
        
        # Search indexing
        index_data = {
            "id": str(created_post.id),
            "title": created_post.title,
            "slug": created_post.slug,
            "summary": created_post.summary,
            "content": plain_text[:5000], # Index first 5000 chars of plain text
            "status": created_post.status
        }
        index_blog_post_task.delay(index_data)
        
        return BlogPostRead.model_validate(created_post)

    async def update_post(self, post_id: UUID, data: BlogPostUpdate) -> BlogPostRead:
        """
        Update blog post, regenerate HTML if JSON changed, and update search index.
        """
        update_data = data.model_dump(exclude_unset=True)
        
        if "content_json" in update_data and update_data["content_json"]:
            # Generate HTML from JSON
            content_html = tiptap_to_html(update_data["content_json"])
            # Sanitize HTML
            update_data["content_html"] = bleach.clean(
                content_html,
                tags=ALLOWED_TAGS,
                attributes=ALLOWED_ATTRS,
            )
            # Recalculate reading time
            plain_text = tiptap_to_text(update_data["content_json"])
            word_count = len(plain_text.split())
            update_data["reading_time_minutes"] = max(1, word_count // 200)
        
        if "title" in update_data and not update_data.get("slug"):
             update_data["slug"] = slugify(update_data["title"])

        updated_post = await self.repo.update(post_id, **update_data)
        if not updated_post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Blog post not found"
            )
            
        # Update search index
        plain_text = tiptap_to_text(updated_post.content_json)
        index_data = {
            "id": str(updated_post.id),
            "title": updated_post.title,
            "slug": updated_post.slug,
            "summary": updated_post.summary,
            "content": plain_text[:5000],
            "status": updated_post.status
        }
        index_blog_post_task.delay(index_data)
        
        return BlogPostRead.model_validate(updated_post)

    async def delete_post(self, post_id: UUID) -> bool:
        """
        Delete blog post and remove from search index.
        """
        success = await self.repo.delete(post_id)
        if success:
            remove_blog_post_from_index_task.delay(str(post_id))
        return success

    async def list_categories(self):
        return await self.repo.get_categories()

async def get_blog_service(repo: BlogRepository = Depends(get_blog_repo)) -> BlogService:
    return BlogService(repo)
