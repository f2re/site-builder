# Module: core/utils.py | Agent: backend-agent | Task: BE-07/slugify
import re
from typing import Optional
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
