# tests/e2e/test_04_shop.py
from playwright.sync_api import Page, expect
from conftest import BASE_URL

def test_shop_page_loads(page: Page):
    page.goto(f"{BASE_URL}/shop")
    page.wait_for_selector("[data-testid='product-card']")
    count = page.locator("[data-testid='product-card']").count()
    assert count >= 2
    page.screenshot(path="tests/e2e/screenshots/04_shop.png")

def test_search_products(page: Page):
    page.goto(f"{BASE_URL}/shop")
    page.fill("[data-testid='search-input']", "OBD2")
    page.wait_for_selector("[data-testid='search-results']", timeout=5000)
    assert page.locator("[data-testid='product-card']").count() >= 1
    page.screenshot(path="tests/e2e/screenshots/04_search.png")

def test_product_detail_page(page: Page):
    page.goto(f"{BASE_URL}/shop")
    page.wait_for_selector("[data-testid='product-card']")
    page.locator("[data-testid='product-card']").first.click()
    page.wait_for_selector("[data-testid='add-to-cart-btn']")
    expect(page.locator("[data-testid='product-price']")).to_be_visible()
    expect(page.locator("[data-testid='product-stock']")).to_be_visible()
    page.screenshot(path="tests/e2e/screenshots/04_product_detail.png")