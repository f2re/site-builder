#!/usr/bin/env python3
"""Seed redirects for OpenCart information pages migrated to blog."""
import asyncio
from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.db.models.blog import BlogPost
from app.db.models.redirect import Redirect


async def seed_information_redirects():
    """Create redirects for information/information URLs → blog posts."""
    async with AsyncSessionLocal() as session:
        # Get all blog posts migrated from oc_information
        stmt = select(BlogPost).where(BlogPost.oc_information_id.is_not(None))
        result = await session.execute(stmt)
        posts = result.scalars().all()

        created = 0
        for post in posts:
            old_path = f"index.php?route=information/information&information_id={post.oc_information_id}"
            new_path = f"/blog/{post.slug}"

            # Check if redirect already exists
            check_stmt = select(Redirect).where(Redirect.old_path == old_path)
            existing = await session.execute(check_stmt)
            if existing.scalar_one_or_none():
                continue

            redirect = Redirect(
                old_path=old_path,
                new_path=new_path,
                status_code=301
            )
            session.add(redirect)
            created += 1

        await session.commit()
        print(f"Created {created} redirects for information pages")


if __name__ == "__main__":
    asyncio.run(seed_information_redirects())
