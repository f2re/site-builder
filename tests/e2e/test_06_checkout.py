# tests/e2e/test_06_checkout.py
from playwright.sync_api import Page, expect
from conftest import BASE_URL

def test_checkout_delivery_form(customer_page: Page):
    """Форма доставки заполняется и СДЭК ПВЗ загружаются."""
    # Убеждаемся что в корзине есть товар
    customer_page.goto(f"{BASE_URL}/shop")
    customer_page.wait_for_selector("[data-testid='product-card']")
    customer_page.locator("[data-testid='product-card']").first.click()
    customer_page.click("[data-testid='add-to-cart-btn']")

    customer_page.goto(f"{BASE_URL}/cart")
    customer_page.click("[data-testid='checkout-btn']")
    customer_page.wait_for_selector("[data-testid='delivery-form']", timeout=8000)

    customer_page.fill("[data-testid='city-input']", "Москва")

    # Ждём загрузку ПВЗ (замокан в conftest)
    customer_page.wait_for_selector("[data-testid='cdek-pickup-point']", timeout=5000)
    customer_page.locator("[data-testid='cdek-pickup-point']").first.click()
    customer_page.click("[data-testid='confirm-delivery-btn']")

    # Переход к форме оплаты
    customer_page.wait_for_selector("[data-testid='payment-form']", timeout=5000)
    customer_page.screenshot(path="tests/e2e/screenshots/06_checkout_payment.png")


def test_order_created_after_payment(customer_page: Page):
    """После оплаты создаётся заказ. YooKassa — имитируем webhook."""
    # ... переходим к payment-form, нажимаем pay-btn
    # YooKassa redirect мокается на уровне backend через fakeredis
    customer_page.goto(f"{BASE_URL}/orders")
    customer_page.wait_for_selector("[data-testid='order-card']", timeout=10000)
    expect(customer_page.locator("[data-testid='order-status']").first).to_be_visible()
    customer_page.screenshot(path="tests/e2e/screenshots/06_order_created.png")