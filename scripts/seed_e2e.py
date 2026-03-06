#!/usr/bin/env python3
"""
Сидирование тестовых данных для E2E тестов.
Запуск: python scripts/seed_e2e.py [--reset] (из корня проекта)
"""
import asyncio
import sys
from pathlib import Path

# Добавить backend в pythonpath
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from app.db.session import AsyncSessionLocal
from app.db.models.user import User
from app.db.models.product import Product, Category
from app.db.models.blog import Post
from app.core.security import get_password_hash
from sqlalchemy import select, delete


# ─── Тестовые данные ──────────────────────────────────────────────────────────

ADMIN = {
    "email": "admin@wifiobd-test.ru",
    "password": "Admin123!",
    "first_name": "Тест",
    "last_name": "Администратор",
    "role": "admin",
}

CUSTOMER = {
    "email": "customer@wifiobd-test.ru",
    "password": "Customer123!",
    "first_name": "Обычный",
    "last_name": "Покупатель",
    "role": "customer",
}

PRODUCTS = [
    {
        "name": "OBD2 адаптер WifiOBD Pro",
        "slug": "obd2-wifiobd-pro",
        "description": "Профессиональный OBD2 адаптер с поддержкой WiFi",
        "price": 2990.00,
        "stock": 50,
        "sku": "WOB-PRO-001",
    },
    {
        "name": "OBD2 адаптер WifiOBD Lite",
        "slug": "obd2-wifiobd-lite",
        "description": "Базовый OBD2 адаптер для личного использования",
        "price": 990.00,
        "stock": 100,
        "sku": "WOB-LIT-001",
    },
    {
        "name": "Тестовый товар для удаления",
        "slug": "test-delete-product",
        "description": "Этот товар будет удалён в тесте",
        "price": 1.00,
        "stock": 1,
        "sku": "TEST-DEL-001",
    },
]

BLOG_POSTS = [
    {
        "title": "Как подключить OBD2 к телефону",
        "slug": "how-to-connect-obd2",
        "content": "Подробная инструкция по подключению OBD2 адаптера к смартфону...",
        "is_published": True,
    },
    {
        "title": "Диагностика автомобиля своими руками",
        "slug": "car-diagnostics-diy",
        "content": "Руководство по самостоятельной диагностике автомобиля...",
        "is_published": True,
    },
]


# ─── Сидер ────────────────────────────────────────────────────────────────────

async def clean_test_data(session):
    """Удаляет предыдущие тестовые данные."""
    test_emails = [ADMIN["email"], CUSTOMER["email"]]
    test_slugs = [p["slug"] for p in PRODUCTS] + [p["slug"] for p in BLOG_POSTS]

    await session.execute(delete(User).where(User.email.in_(test_emails)))
    await session.execute(delete(Product).where(Product.slug.in_(test_slugs)))
    await session.execute(delete(Post).where(Post.slug.in_(test_slugs)))
    await session.commit()
    print("🧹 Старые тестовые данные очищены")


async def create_user(session, data: dict) -> User:
    result = await session.execute(select(User).where(User.email == data["email"]))
    existing = result.scalar_one_or_none()
    if existing:
        return existing

    user = User(
        email=data["email"],
        password_hash=get_password_hash(data["password"]),
        first_name=data["first_name"],
        last_name=data["last_name"],
        role=data["role"],
        is_active=True,
        is_verified=True,  # пропускаем email-верификацию для тестов
    )
    session.add(user)
    await session.flush()
    return user


async def seed():
    async with AsyncSessionLocal() as session:
        reset = "--reset" in sys.argv
        if reset:
            await clean_test_data(session)

        # 1. Пользователи
        admin = await create_user(session, ADMIN)
        customer = await create_user(session, CUSTOMER)
        await session.commit()
        print(f"✅ Admin: {ADMIN['email']} / {ADMIN['password']}")
        print(f"✅ Customer: {CUSTOMER['email']} / {CUSTOMER['password']}")

        # 2. Категория для товаров
        result = await session.execute(
            select(Category).where(Category.slug == "obd-adapters")
        )
        category = result.scalar_one_or_none()
        if not category:
            category = Category(
                name="OBD Адаптеры",
                slug="obd-adapters",
                description="Адаптеры для диагностики автомобиля",
            )
            session.add(category)
            await session.flush()

        # 3. Товары
        for p_data in PRODUCTS:
            result = await session.execute(
                select(Product).where(Product.slug == p_data["slug"])
            )
            if not result.scalar_one_or_none():
                product = Product(
                    **p_data,
                    category_id=category.id,
                    is_active=True,
                )
                session.add(product)
        await session.commit()
        print(f"✅ Создано товаров: {len(PRODUCTS)}")

        # 4. Блог-посты
        for post_data in BLOG_POSTS:
            result = await session.execute(
                select(Post).where(Post.slug == post_data["slug"])
            )
            if not result.scalar_one_or_none():
                post = Post(**post_data, author_id=admin.id)
                session.add(post)
        await session.commit()
        print(f"✅ Создано блог-постов: {len(BLOG_POSTS)}")

        print("\n🚀 Тестовые данные готовы. Запускай: pytest tests/e2e/ -v --headed")


if __name__ == "__main__":
    asyncio.run(seed())
