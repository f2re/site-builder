# Module: core/utils.py | Agent: backend-agent | Task: bugfix_backend_product_002
import re
from typing import Optional, Any
from slugify import slugify
import bleach

def generate_slug(text: str, current_slug: Optional[str] = None) -> str:
    """
    Generate a slug from text if current_slug is missing or contains non-latin characters.
    Uses python-slugify which handles Cyrillic -> Latin transliteration.
    """
    # If slug is provided and is valid latin-only (plus hyphens/underscores), return it
    if current_slug and re.match(r'^[a-z0-9\-_]+$', current_slug):
        return current_slug
    
    # If current_slug is provided but has Cyrillic/etc, slugify it
    if current_slug:
        return slugify(current_slug)
        
    # Otherwise slugify the text (usually title/name)
    return slugify(text)

_TIPTAP_ALLOWED_TAGS = {
    "p", "h2", "h3", "ul", "ol", "li", "img",
    "strong", "em", "code", "br",
}
_TIPTAP_ALLOWED_ATTRS = {
    "img": ["src", "alt", "width", "height"],
    "*": [],
}


def _render_inline(node: dict) -> str:
    """Render a TipTap inline text node with marks to HTML."""
    text = node.get("text", "")
    for mark in node.get("marks", []):
        mark_type = mark.get("type", "")
        if mark_type == "bold":
            text = f"<strong>{text}</strong>"
        elif mark_type == "italic":
            text = f"<em>{text}</em>"
        elif mark_type == "code":
            text = f"<code>{text}</code>"
    return text


def _render_node(node: dict) -> str:
    """Recursively render a TipTap AST node to an HTML string."""
    node_type = node.get("type", "")

    if node_type == "text":
        return _render_inline(node)

    children_html = "".join(_render_node(c) for c in node.get("content", []))

    if node_type == "paragraph":
        return f"<p>{children_html}</p>"
    if node_type == "heading":
        level = node.get("attrs", {}).get("level", 2)
        tag = "h2" if level <= 2 else "h3"
        return f"<{tag}>{children_html}</{tag}>"
    if node_type == "bulletList":
        return f"<ul>{children_html}</ul>"
    if node_type == "orderedList":
        return f"<ol>{children_html}</ol>"
    if node_type == "listItem":
        return f"<li>{children_html}</li>"
    if node_type == "image":
        attrs = node.get("attrs", {})
        src = attrs.get("src", "")
        alt = attrs.get("alt", "")
        width = attrs.get("width", "")
        height = attrs.get("height", "")
        parts = [f'src="{src}"', f'alt="{alt}"']
        if width:
            parts.append(f'width="{width}"')
        if height:
            parts.append(f'height="{height}"')
        return f'<img {" ".join(parts)}>'
    if node_type == "hardBreak":
        return "<br>"

    # For unknown block types — just render children
    return children_html


def tiptap_json_to_html(content: Any) -> str:
    """
    Convert a TipTap JSON AST to a sanitized HTML string.
    Supports: paragraph, heading (h2/h3), bulletList, orderedList, listItem,
    image, hardBreak, and inline marks bold/italic/code.
    Output is sanitized via bleach.
    """
    if not isinstance(content, dict) or "content" not in content:
        return ""

    raw_html = "".join(_render_node(node) for node in content.get("content", []))

    return bleach.clean(
        raw_html,
        tags=_TIPTAP_ALLOWED_TAGS,
        attributes=_TIPTAP_ALLOWED_ATTRS,
        strip=True,
    )


def extract_text_from_tiptap(content: Any, max_len: int = 500) -> str:
    """
    Extract first text block from TipTap JSON structure for SEO description.
    """
    if not isinstance(content, dict) or "content" not in content:
        return ""
    
    texts = []
    for node in content.get("content", []):
        if node.get("type") == "paragraph" and "content" in node:
            p_text = "".join([t.get("text", "") for t in node.get("content", []) if t.get("type") == "text"])
            if p_text:
                texts.append(p_text)
        
        if len(" ".join(texts)) >= max_len:
            break
            
    full_text = " ".join(texts).strip()
    if len(full_text) > max_len:
        return full_text[:max_len-3].strip() + "..."
    return full_text
