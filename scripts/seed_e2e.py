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
from app.db.models.product import Product, Category, ProductVariant
from app.db.models.blog import BlogPost as Post, BlogPostStatus, Author
from app.core.security import get_password_hash, encrypt_data, get_blind_index
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
        "stock_quantity": 50,
        "sku": "WOB-PRO-001",
    },
    {
        "name": "OBD2 адаптер WifiOBD Lite",
        "slug": "obd2-wifiobd-lite",
        "description": "Базовый OBD2 адаптер для личного использования",
        "price": 990.00,
        "stock_quantity": 100,
        "sku": "WOB-LIT-001",
    },
    {
        "name": "Тестовый товар для удаления",
        "slug": "test-delete-product",
        "description": "Этот товар будет удалён в тесте",
        "price": 1.00,
        "stock_quantity": 1,
        "sku": "TEST-DEL-001",
    },
]

BLOG_POSTS = [
    {
        "title": "Как подключить OBD2 к телефону",
        "slug": "how-to-connect-obd2",
        "content_html": "<p>Подробная инструкция по подключению OBD2 адаптера к смартфону...</p>",
        "status": BlogPostStatus.PUBLISHED,
    },
    {
        "title": "Диагностика автомобиля своими руками",
        "slug": "car-diagnostics-diy",
        "content_html": "<p>Руководство по самостоятельной диагностике автомобиля...</p>",
        "status": BlogPostStatus.PUBLISHED,
    },
]


# ─── Сидер ────────────────────────────────────────────────────────────────────

async def clean_test_data(session):
    """Удаляет предыдущие тестовые данные."""
    test_emails = [ADMIN["email"], CUSTOMER["email"]]
    test_email_hashes = [get_blind_index(email) for email in test_emails]
    test_slugs = [p["slug"] for p in PRODUCTS] + [p["slug"] for p in BLOG_POSTS]

    await session.execute(delete(User).where(User.email_hash.in_(test_email_hashes)))
    await session.execute(delete(Product).where(Product.slug.in_(test_slugs)))
    await session.execute(delete(Post).where(Post.slug.in_(test_slugs)))
    await session.commit()
    print("🧹 Старые тестовые данные очищены")


async def create_user(session, data: dict) -> User:
    # Use unencrypted email for the check
    result = await session.execute(select(User).where(User.email_hash == get_blind_index(data["email"])))
    existing = result.scalar_one_or_none()
    if existing:
        # For idempotency, we can choose to return the existing user
        # or update them. For seeding, returning is safer.
        return existing

    user = User(
        email_hash=get_blind_index(data["email"]),
        email=encrypt_data(data["email"]),
        hashed_password=get_password_hash(data["password"]),
        full_name=f"{data['first_name']} {data['last_name']}",
        role=data["role"],
        is_active=True,
        is_superuser=data["role"] == "admin"
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

        # Create an author profile for the admin user
        result = await session.execute(select(Author).where(Author.user_id == admin.id))
        author = result.scalar_one_or_none()
        if not author:
            author = Author(
                user_id=admin.id,
                display_name=admin.full_name or "Admin"
            )
            session.add(author)
            await session.commit()
            await session.refresh(author)
        
        print(f"✅ Author created for admin: {author.display_name}")

        # 2. Категория для товаров
        result = await session.execute(
            select(Category).where(Category.slug == "obd-adapters")
        )
        category = result.scalar_one_or_none()
        if not category:
            category = Category(
                name="OBD Адаптеры",
                slug="obd-adapters",
            )
            session.add(category)
            await session.flush()

        # 3. Товары
        for p_data in PRODUCTS:
            result = await session.execute(
                select(Product).where(Product.slug == p_data["slug"])
            )
            if not result.scalar_one_or_none():
                product_data = p_data.copy()
                variant_data = {
                    "price": product_data.pop("price"),
                    "stock_quantity": product_data.pop("stock_quantity"),
                    "sku": product_data.pop("sku"),
                    "name": product_data.get("name")
                }

                product = Product(
                    name=product_data["name"],
                    slug=product_data["slug"],
                    description=product_data["description"],
                    category_id=category.id,
                    is_active=True,
                )
                session.add(product)
                await session.flush()

                variant = ProductVariant(product_id=product.id, **variant_data)
                session.add(variant)
        await session.commit()
        print(f"✅ Создано товаров: {len(PRODUCTS)}")

        # 4. Блог-посты
        for post_data in BLOG_POSTS:
            result = await session.execute(
                select(Post).where(Post.slug == post_data["slug"])
            )
            if not result.scalar_one_or_none():
                post = Post(**post_data, author_id=author.id)
                session.add(post)
        await session.commit()
        print(f"✅ Создано блог-постов: {len(BLOG_POSTS)}")

        print("\n🚀 Тестовые данные готовы. Запускай: pytest tests/e2e/ -v --headed")


if __name__ == "__main__":
    asyncio.run(seed())
