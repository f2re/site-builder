import asyncio
import sys
import os

# Добавляем /app в PYTHONPATH для импортов
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.db.models.page import StaticPage

async def seed():
    pages = [
        {"slug": "about", "title": "О нас", "content": "<h1>О нас</h1><p>Контент страницы...</p>", "is_active": True},
        {"slug": "contacts", "title": "Контакты", "content": "<h1>Контакты</h1><p>Контент страницы...</p>", "is_active": True},
        {"slug": "faq", "title": "Вопросы и ответы", "content": "<h1>FAQ</h1><p>Контент страницы...</p>", "is_active": True},
        {"slug": "returns", "title": "Возврат товара", "content": "<h1>Возврат</h1><p>Контент страницы...</p>", "is_active": True},
        {"slug": "privacy", "title": "Политика конфиденциальности", "content": "<h1>Политика конфиденциальности</h1><p>Контент страницы...</p>", "is_active": True},
        {"slug": "shipping", "title": "Доставка и оплата", "content": "<h1>Доставка и оплата</h1><p>Контент страницы...</p>", "is_active": True},
    ]
    async with AsyncSessionLocal() as session:
        for p in pages:
            stmt = select(StaticPage).where(StaticPage.slug == p["slug"])
            res = await session.execute(stmt)
            if not res.scalar_one_or_none():
                session.add(StaticPage(**p))
                print(f"Adding page: {p['slug']}")
            else:
                print(f"Page already exists: {p['slug']}")
        await session.commit()
        print("Seeding completed successfully.")

if __name__ == "__main__":
    asyncio.run(seed())
