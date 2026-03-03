# Module: core/utils.py | Agent: backend-agent | Task: BE-07/slugify
import re
from typing import Optional, Any
from slugify import slugify

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
