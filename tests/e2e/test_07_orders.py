# tests/e2e/test_07_orders.py
from playwright.sync_api import Page, expect
from conftest import BASE_URL

def test_orders_page_shows_history(customer_page: Page):
    """Страница заказов пользователя показывает историю."""
    customer_page.goto(f"{BASE_URL}/account/orders")
    customer_page.wait_for_selector("[data-testid='order-list']", timeout=8000)

    orders = customer_page.locator("[data-testid='order-card']")
    assert orders.count() >= 1

    # Проверяем обязательные поля каждого заказа
    first_order = orders.first
    expect(first_order.locator("[data-testid='order-number']")).to_be_visible()
    expect(first_order.locator("[data-testid='order-status']")).to_be_visible()
    customer_page.screenshot(path="tests/e2e/screenshots/07_orders.png")


def test_order_detail_page(customer_page: Page):
    """Открытие детальной страницы заказа."""
    customer_page.goto(f"{BASE_URL}/account/orders")
    customer_page.wait_for_selector("[data-testid='order-card']")
    customer_page.locator("[data-testid='order-card']").first.click()

    customer_page.wait_for_selector("[data-testid='order-items']", timeout=5000)
    expect(customer_page.locator("[data-testid='order-status']")).to_be_visible()
    customer_page.screenshot(path="tests/e2e/screenshots/07_order_detail.png")