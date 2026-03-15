# Module: api/v1/blog/service.py | Agent: backend-agent | Task: p28_backend_blog_categories
import bleach
from typing import List, Optional, Any, Union
from uuid import UUID
from datetime import datetime, timezone
from fastapi import Depends, HTTPException, status
import structlog

from app.api.v1.blog.repository import BlogRepository, get_blog_repo
from app.api.v1.blog.schemas import (
    BlogCategoryCreate,
    BlogCategoryRead,
    BlogCategoryUpdate,
    BlogPostCreate,
    BlogPostUpdate,
    BlogPagination,
    BlogPostRead,
    CommentCreate,
    CommentRead,
    CommentAdminRead,
    TagRead,
    BlogPostShortRead,
)
from app.db.models.blog import BlogCategory, BlogPost, BlogPostStatus, Comment, CommentStatus, Author, Tag
from app.tasks.search import index_blog_post_task, remove_blog_post_from_index_task
from app.core.security import encrypt_data, decrypt_data
from app.core.utils import generate_slug

logger = structlog.get_logger()

# HTML sanitization config
ALLOWED_TAGS = bleach.sanitizer.ALLOWED_TAGS | {
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'p', 'br', 'ul', 'ol', 'li',
    'strong', 'em', 'b', 'i', 'u',
    'blockquote', 'code', 'pre',
    'img', 'figure', 'figcaption',
    'a', 'table', 'thead', 'tbody', 'tr', 'th', 'td',
    'iframe',
    'div',
}
ALLOWED_ATTRS = {
    'a': ['href', 'title', 'rel', 'target'],
    'img': ['src', 'alt', 'width', 'height', 'loading', 'class'],
    '*': ['class'],
    'iframe': [
        'src', 'width', 'height', 'frameborder', 'allowfullscreen',
        'allow', 'scrolling', 'style', 'title', 'id', 'class',
    ],
    'div': ['class', 'style'],
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

    async def _sync_tags(self, post: BlogPost, tag_names: List[str]) -> None:
        """Synchronize post tags (create new tags if they don't exist)."""
        tags = []
        for name in tag_names:
            name = name.strip()
            if not name:
                continue
            
            tag = await self.repo.get_tag_by_name(name)
            if not tag:
                # Use name for slug too, generate_slug will clean it
                tag = Tag(name=name, slug=generate_slug(name))
                tag = await self.repo.create_tag(tag)
            tags.append(tag)
        
        post.tags = tags

    async def list_posts(
        self,
        category_slug: Optional[str] = None,
        tag_slug: Optional[str] = None,
        status: Optional[BlogPostStatus] = BlogPostStatus.PUBLISHED,
        is_featured: Optional[bool] = None,
        cursor: Optional[str] = None,
        per_page: int = 20,
        section: Optional[str] = None,
    ) -> BlogPagination:
        items, next_cursor, total = await self.repo.list_posts(
            category_slug=category_slug,
            tag_slug=tag_slug,
            status=status,
            is_featured=is_featured,
            cursor=cursor,
            per_page=per_page,
            section=section,
        )
        short_items = []
        for post in items:
            item = BlogPostShortRead.model_validate(post)
            item.cover_url = post.cover_image
            item.excerpt = post.summary
            item.reading_time_minutes = post.reading_time
            if not item.carousel_images and hasattr(post, "carousel_images") and post.carousel_images:
                item.carousel_images = list(post.carousel_images)
            short_items.append(item)
        return BlogPagination(
            items=short_items,
            next_cursor=next_cursor,
            total=total
        )

    def _enrich_post_read(self, post: BlogPost, result: BlogPostRead) -> BlogPostRead:
        """Fill frontend-compatible alias fields on BlogPostRead."""
        result.cover_url = post.cover_image
        result.excerpt = post.summary
        result.reading_time_minutes = post.reading_time
        if not result.og_image_url:
            carousel = list(post.carousel_images) if post.carousel_images else []
            result.og_image_url = (carousel[0] if carousel else None) or post.cover_image
        return result

    async def get_post_detail(self, slug: str, is_admin: bool = False) -> BlogPostRead:
        post = await self.repo.get_by_slug(slug)
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Blog post not found"
            )
        if post.status in (BlogPostStatus.DRAFT, BlogPostStatus.ARCHIVED) and not is_admin:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found"
            )
        result = BlogPostRead.model_validate(post)
        return self._enrich_post_read(post, result)

    async def get_or_create_author(self, user_id: UUID, display_name: str = "Anonymous") -> Author:
        author = await self.repo.get_author_by_user_id(user_id)
        if not author:
            author = Author(
                user_id=user_id,
                display_name=display_name
            )
            author = await self.repo.create_author(author)
        return author

    async def create_post(self, data: BlogPostCreate, user_id: UUID) -> BlogPostRead:
        """
        Create a new blog post, generate HTML from JSON, calculate reading time, and index in search.
        """
        slug = generate_slug(data.title, data.slug)
        
        # Ensure author exists for this user
        author = await self.get_or_create_author(user_id, display_name=data.title)
        
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
        
        published_at = None
        if data.status == BlogPostStatus.PUBLISHED:
            published_at = datetime.now(timezone.utc)

        post = BlogPost(
            title=data.title,
            slug=slug,
            summary=data.summary,
            content_json=data.content_json,
            content_html=content_html,
            status=data.status,
            is_featured=data.is_featured,
            category_id=data.category_id,
            author_id=author.id,
            cover_image=data.cover_image,
            og_image_url=data.og_image_url,
            carousel_images=data.carousel_images or [],
            meta_title=data.meta_title,
            meta_description=data.meta_description,
            reading_time=reading_time,
            published_at=published_at
        )
        
        if data.tags:
            await self._sync_tags(post, data.tags)
        
        created_post = await self.repo.create(post)
        await self.repo.session.commit()
        
        # Search indexing
        index_data = {
            "id": str(created_post.id),
            "title": created_post.title,
            "slug": created_post.slug,
            "summary": created_post.summary,
            "content": plain_text[:5000],
            "status": created_post.status
        }
        try:
            index_blog_post_task.delay(index_data)
        except Exception as exc:
            logger.warning("search_index_task_failed", post_id=str(created_post.id), error=str(exc))

        # Reload with relationships to avoid MissingGreenlet during validation
        loaded_post = await self.repo.get_by_id(created_post.id)
        if not loaded_post:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found after creation")
        result = BlogPostRead.model_validate(loaded_post)
        return self._enrich_post_read(loaded_post, result)

    async def update_post(self, post_id: UUID, data: BlogPostUpdate) -> BlogPostRead:
        """
        Update blog post, regenerate HTML if JSON changed, and update search index.
        """
        post = await self.repo.get_by_id(post_id)
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Blog post not found"
            )

        update_data = data.model_dump(exclude_unset=True)
        
        # 1. Sync tags
        if "tags" in update_data:
            tag_names = update_data.pop("tags")
            if tag_names is not None:
                await self._sync_tags(post, tag_names)

        # 2. Handle status and published_at
        if "status" in update_data:
            new_status = update_data["status"]
            if new_status == BlogPostStatus.PUBLISHED and post.status != BlogPostStatus.PUBLISHED:
                post.published_at = datetime.now(timezone.utc)
            post.status = new_status
            del update_data["status"]

        # 3. Handle content (JSON or HTML)
        if "content_json" in update_data and update_data["content_json"]:
            post.content_json = update_data["content_json"]
            # Generate HTML from JSON
            content_html = tiptap_to_html(update_data["content_json"])
            # Sanitize HTML
            post.content_html = bleach.clean(
                content_html,
                tags=ALLOWED_TAGS,
                attributes=ALLOWED_ATTRS,
            )
            # Recalculate reading time
            plain_text = tiptap_to_text(update_data["content_json"])
            word_count = len(plain_text.split())
            post.reading_time = max(1, word_count // 200)
            del update_data["content_json"]
        elif "content_html" in update_data and update_data["content_html"]:
            # Direct HTML update (sanitize first)
            post.content_html = bleach.clean(
                update_data["content_html"],
                tags=ALLOWED_TAGS,
                attributes=ALLOWED_ATTRS,
            )
            del update_data["content_html"]

        # 4. Handle slug generation if title or slug changed
        if "title" in update_data or "slug" in update_data:
            title = update_data.get("title", post.title)
            slug = update_data.get("slug", post.slug)
            post.slug = generate_slug(title, slug)
            if "title" in update_data:
                post.title = update_data.pop("title")
            if "slug" in update_data:
                del update_data["slug"]

        # 5. Apply remaining fields
        for key, value in update_data.items():
            setattr(post, key, value)

        await self.repo.session.commit()
            
        # 6. Update search index
        # Fallback text if JSON is missing or empty
        plain_text = tiptap_to_text(post.content_json) if post.content_json else ""
        if not plain_text and post.content_html:
            # Very crude strip tags for HTML if JSON is not available
            plain_text = post.content_html[:5000]

        index_data = {
            "id": str(post.id),
            "title": post.title,
            "slug": post.slug,
            "summary": post.summary,
            "content": plain_text[:5000],
            "status": post.status
        }
        try:
            index_blog_post_task.delay(index_data)
        except Exception as exc:
            logger.warning("search_index_task_failed", post_id=str(post.id), error=str(exc))

        # Reload with relationships to avoid MissingGreenlet
        loaded_post = await self.repo.get_by_id(post.id)
        if not loaded_post:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found after update")
        result = BlogPostRead.model_validate(loaded_post)
        return self._enrich_post_read(loaded_post, result)

    async def delete_post(self, post_id_or_slug: Union[UUID, str]) -> bool:
        """
        Delete blog post and remove from search index.
        Supports both UUID and slug string.
        """
        if isinstance(post_id_or_slug, UUID):
            post = await self.repo.get_by_id(post_id_or_slug)
            success = await self.repo.delete(post_id_or_slug)
        else:
            # Check if it's a UUID string
            try:
                actual_id = UUID(post_id_or_slug)
                post = await self.repo.get_by_id(actual_id)
                success = await self.repo.delete(actual_id)
            except ValueError:
                # It's a slug
                post = await self.repo.get_by_slug(post_id_or_slug)
                success = await self.repo.delete_by_slug(post_id_or_slug)

        if success and post:
            await self.repo.session.commit()
            try:
                remove_blog_post_from_index_task.delay(str(post.id))
            except Exception as exc:
                logger.warning("search_index_removal_failed", post_id=str(post.id), error=str(exc))
        return success

    async def list_categories(self, section: Optional[str] = None) -> List[BlogCategoryRead]:
        rows = await self.repo.get_categories_with_count(section=section)
        result = []
        for category, posts_count in rows:
            cat_read = BlogCategoryRead.model_validate(category)
            cat_read.posts_count = posts_count
            result.append(cat_read)
        return result

    async def create_category(self, data: BlogCategoryCreate) -> BlogCategoryRead:
        from app.core.utils import generate_slug
        slug = generate_slug(data.name, data.slug) if data.slug else generate_slug(data.name)
        category = BlogCategory(
            name=data.name,
            slug=slug,
            description=data.description,
            section=data.section,
        )
        created = await self.repo.create_category(category)
        await self.repo.session.commit()
        cat_read = BlogCategoryRead.model_validate(created)
        cat_read.posts_count = 0
        return cat_read

    async def update_category(self, category_id: UUID, data: BlogCategoryUpdate) -> BlogCategoryRead:
        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="No fields to update")
        updated = await self.repo.update_category(category_id, **update_data)
        if not updated:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
        await self.repo.session.commit()
        # Reload with count
        rows = await self.repo.get_categories_with_count()
        for category, posts_count in rows:
            if category.id == category_id:
                cat_read = BlogCategoryRead.model_validate(category)
                cat_read.posts_count = posts_count
                return cat_read
        cat_read = BlogCategoryRead.model_validate(updated)
        cat_read.posts_count = 0
        return cat_read

    async def delete_category(self, category_id: UUID) -> bool:
        success = await self.repo.delete_category(category_id)
        if success:
            await self.repo.session.commit()
        return success

    async def get_tags(self) -> List[TagRead]:
        tags = await self.repo.get_all_tags()
        return [TagRead.model_validate(tag) for tag in tags]

    async def create_comment(self, post_id: UUID, data: CommentCreate) -> CommentRead:
        encrypted_email = encrypt_data(data.author_email)
        comment = Comment(
            post_id=post_id,
            author_name=data.author_name,
            author_email=encrypted_email,
            body=data.body,
            status=CommentStatus.PENDING
        )
        created_comment = await self.repo.create_comment(comment)
        await self.repo.session.commit()
        return CommentRead.model_validate(created_comment)

    async def get_comments(self, post_id: UUID, is_admin: bool = False) -> Union[List[CommentRead], List[CommentAdminRead]]:
        status_filter = None if is_admin else CommentStatus.APPROVED
        comments = await self.repo.get_comments_by_post_id(post_id, status=status_filter)
        
        if is_admin:
            results = []
            for c in comments:
                c_data = CommentAdminRead.model_validate(c)
                c_data.author_email = decrypt_data(c.author_email)
                results.append(c_data)
            return results
        
        return [CommentRead.model_validate(c) for c in comments]

    async def approve_comment(self, comment_id: UUID) -> CommentAdminRead:
        updated_comment = await self.repo.update_comment_status(comment_id, CommentStatus.APPROVED)
        if not updated_comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Comment not found"
            )
        await self.repo.session.commit()
        res = CommentAdminRead.model_validate(updated_comment)
        res.author_email = decrypt_data(updated_comment.author_email)
        return res

    async def delete_comment(self, comment_id: UUID) -> bool:
        success = await self.repo.delete_comment(comment_id)
        if success:
            await self.repo.session.commit()
        return success

    async def get_pending_comments(self) -> List[CommentAdminRead]:
        comments = await self.repo.get_pending_comments()
        results = []
        for c in comments:
            c_data = CommentAdminRead.model_validate(c)
            c_data.author_email = decrypt_data(c.author_email)
            results.append(c_data)
        return results

async def get_blog_service(repo: BlogRepository = Depends(get_blog_repo)) -> BlogService:
    return BlogService(repo)
