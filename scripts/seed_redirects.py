# Script: scripts/seed_redirects.py | Agent: backend-agent | Task: p15_backend_redirect_fix
"""Seed redirect records from OpenCart database into the new site's redirects table.

Usage:
    python scripts/seed_redirects.py [--dry-run]

Environment variables (or .env file):
    OC_DB_HOST, OC_DB_PORT, OC_DB_USER, OC_DB_PASSWORD, OC_DB_NAME
    OC_LANGUAGE_ID  (default: 1)
    DATABASE_URL    (PostgreSQL connection string)

The script is idempotent: running it multiple times does not create duplicate records.
It uses INSERT ... ON CONFLICT DO UPDATE to upsert redirect rows.
"""

import argparse
import asyncio
import re
import sys
from pathlib import Path

# Allow importing backend app modules when running from project root
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.core.config import settings
from app.db.models.redirect import Redirect
from app.db.models.product import Category, Product
from app.db.opencart_models import (
    OCCategory,
    OCCategoryDescription,
    OCInformation,
    OCInformationDescription,
    OCProduct,
    OCProductDescription,
)


def _slugify(text_value: str) -> str:
    """Convert arbitrary text to a URL-safe slug."""
    value = text_value.lower().strip()
    # Replace Cyrillic characters with latin transliteration
    cyrillic_map = {
        "а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "е": "e", "ё": "yo",
        "ж": "zh", "з": "z", "и": "i", "й": "y", "к": "k", "л": "l", "м": "m",
        "н": "n", "о": "o", "п": "p", "р": "r", "с": "s", "т": "t", "у": "u",
        "ф": "f", "х": "kh", "ц": "ts", "ч": "ch", "ш": "sh", "щ": "shch",
        "ъ": "", "ы": "y", "ь": "", "э": "e", "ю": "yu", "я": "ya",
    }
    result = "".join(cyrillic_map.get(c, c) for c in value)
    result = re.sub(r"[^a-z0-9]+", "-", result)
    result = result.strip("-")
    return result or "page"


async def _get_oc_session(oc_db_url: str) -> async_sessionmaker[AsyncSession]:
    oc_engine = create_async_engine(oc_db_url, pool_pre_ping=True)
    return async_sessionmaker(oc_engine, expire_on_commit=False)


async def _upsert_redirect(
    pg_session: AsyncSession,
    old_path: str,
    new_path: str,
    status_code: int = 301,
    dry_run: bool = False,
) -> bool:
    """Insert or update a redirect row. Returns True if a change was made."""
    if not old_path.startswith("/"):
        old_path = "/" + old_path

    if dry_run:
        print(f"  [DRY-RUN] {old_path!r} -> {new_path!r}")
        return True

    stmt = (
        pg_insert(Redirect)
        .values(old_path=old_path, new_path=new_path, status_code=status_code)
        .on_conflict_do_update(
            index_elements=["old_path"],
            set_={"new_path": new_path, "status_code": status_code},
        )
    )
    await pg_session.execute(stmt)
    return True


async def _load_new_category_slugs(pg_session: AsyncSession) -> dict[int, str]:
    """Return mapping: oc_category_id -> slug from new site categories table."""
    result = await pg_session.execute(
        select(Category.oc_category_id, Category.slug).where(
            Category.oc_category_id.is_not(None)
        )
    )
    return {row.oc_category_id: row.slug for row in result}


async def _load_new_product_slugs(pg_session: AsyncSession) -> dict[int, str]:
    """Return mapping: oc_product_id -> slug from new site products table."""
    result = await pg_session.execute(
        select(Product.oc_product_id, Product.slug).where(
            Product.oc_product_id.is_not(None)
        )
    )
    return {row.oc_product_id: row.slug for row in result}


async def seed_category_redirects(
    oc_session: AsyncSession,
    pg_session: AsyncSession,
    language_id: int,
    dry_run: bool,
) -> int:
    """Generate redirects for OpenCart categories."""
    count = 0

    # Load all categories from OC
    cats_result = await oc_session.execute(select(OCCategory))
    categories = {cat.category_id: cat for cat in cats_result.scalars()}

    # Load category descriptions for target language
    descs_result = await oc_session.execute(
        select(OCCategoryDescription).where(
            OCCategoryDescription.language_id == language_id
        )
    )
    descs = {d.category_id: d for d in descs_result.scalars()}

    # Load new-site slugs by oc_category_id
    cat_slugs = await _load_new_category_slugs(pg_session)

    for cat_id, cat in categories.items():
        desc = descs.get(cat_id)
        if desc is None:
            # Fall back to first available description
            any_desc_result = await oc_session.execute(
                select(OCCategoryDescription).where(
                    OCCategoryDescription.category_id == cat_id
                ).limit(1)
            )
            desc = any_desc_result.scalar_one_or_none()

        # Determine new_path
        if cat_id in cat_slugs:
            new_path = f"/catalog/{cat_slugs[cat_id]}"
        elif desc:
            new_path = f"/catalog/{_slugify(desc.name)}"
        else:
            new_path = f"/catalog/category-{cat_id}"

        # old_path without parent: /index.php?route=product/category&path=<cat_id>
        old_path_simple = f"/index.php?route=product/category&path={cat_id}"
        changed = await _upsert_redirect(pg_session, old_path_simple, new_path, dry_run=dry_run)
        if changed:
            count += 1

        # old_path with parent: /index.php?route=product/category&path=<parent>_<cat_id>
        if cat.parent_id and cat.parent_id != 0:
            old_path_nested = (
                f"/index.php?route=product/category&path={cat.parent_id}_{cat_id}"
            )
            changed = await _upsert_redirect(pg_session, old_path_nested, new_path, dry_run=dry_run)
            if changed:
                count += 1

    return count


async def seed_product_redirects(
    oc_session: AsyncSession,
    pg_session: AsyncSession,
    language_id: int,
    dry_run: bool,
) -> int:
    """Generate redirects for OpenCart products."""
    count = 0

    prods_result = await oc_session.execute(select(OCProduct))
    products = {p.product_id: p for p in prods_result.scalars()}

    descs_result = await oc_session.execute(
        select(OCProductDescription).where(
            OCProductDescription.language_id == language_id
        )
    )
    descs = {d.product_id: d for d in descs_result.scalars()}

    prod_slugs = await _load_new_product_slugs(pg_session)

    for prod_id in products:
        desc = descs.get(prod_id)

        if prod_id in prod_slugs:
            new_path = f"/shop/{prod_slugs[prod_id]}"
        elif desc:
            new_path = f"/shop/{_slugify(desc.name)}"
        else:
            new_path = f"/shop/product-{prod_id}"

        old_path = f"/index.php?route=product/product&product_id={prod_id}"
        changed = await _upsert_redirect(pg_session, old_path, new_path, dry_run=dry_run)
        if changed:
            count += 1

    return count


async def seed_information_redirects(
    oc_session: AsyncSession,
    pg_session: AsyncSession,
    language_id: int,
    dry_run: bool,
) -> int:
    """Generate redirects for OpenCart information (static) pages -> /blog/<slug>."""
    count = 0

    infos_result = await oc_session.execute(select(OCInformation))
    infos = {i.information_id: i for i in infos_result.scalars()}

    descs_result = await oc_session.execute(
        select(OCInformationDescription).where(
            OCInformationDescription.language_id == language_id
        )
    )
    descs = {d.information_id: d for d in descs_result.scalars()}

    for info_id in infos:
        desc = descs.get(info_id)
        if desc:
            slug = _slugify(desc.title)
        else:
            slug = f"info-{info_id}"

        new_path = f"/blog/{slug}"
        old_path = (
            f"/index.php?route=information/information&information_id={info_id}"
        )
        changed = await _upsert_redirect(pg_session, old_path, new_path, dry_run=dry_run)
        if changed:
            count += 1

    return count


async def main(dry_run: bool, oc_db_url: str | None) -> None:
    if oc_db_url is None:
        oc_db_url = (
            f"mysql+aiomysql://{settings.OC_DB_USER}:{settings.OC_DB_PASSWORD}"
            f"@{settings.OC_DB_HOST}:{settings.OC_DB_PORT}/{settings.OC_DB_NAME}"
        )

    pg_engine = create_async_engine(settings.DATABASE_URL, pool_pre_ping=True)
    pg_session_factory = async_sessionmaker(pg_engine, expire_on_commit=False)

    oc_engine = create_async_engine(oc_db_url, pool_pre_ping=True)
    oc_session_factory = async_sessionmaker(oc_engine, expire_on_commit=False)

    language_id = settings.OC_LANGUAGE_ID

    if dry_run:
        print("=== DRY RUN MODE — no changes will be written ===")

    async with oc_session_factory() as oc_session, pg_session_factory() as pg_session:
        print(f"Seeding category redirects (language_id={language_id})...")
        n_cats = await seed_category_redirects(oc_session, pg_session, language_id, dry_run)
        print(f"  {n_cats} category redirect(s) processed.")

        print("Seeding product redirects...")
        n_prods = await seed_product_redirects(oc_session, pg_session, language_id, dry_run)
        print(f"  {n_prods} product redirect(s) processed.")

        print("Seeding information page redirects...")
        n_info = await seed_information_redirects(oc_session, pg_session, language_id, dry_run)
        print(f"  {n_info} information redirect(s) processed.")

        if not dry_run:
            await pg_session.commit()
            print("Changes committed to PostgreSQL.")

    total = n_cats + n_prods + n_info
    print(f"\nDone. Total rows processed: {total}")

    await pg_engine.dispose()
    await oc_engine.dispose()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Seed OpenCart redirects into new site redirects table."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would be inserted without writing to the database.",
    )
    parser.add_argument(
        "--oc-db-url",
        default=None,
        help=(
            "MySQL OpenCart DB URL (mysql+aiomysql://user:pass@host:port/db). "
            "If omitted, reads OC_DB_* from environment / .env file."
        ),
    )
    args = parser.parse_args()
    asyncio.run(main(dry_run=args.dry_run, oc_db_url=args.oc_db_url))
