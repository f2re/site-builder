# tests/e2e/test_05_cart.py
from playwright.sync_api import Page, expect
from conftest import BASE_URL

def test_add_to_cart(customer_page: Page):
    """Покупатель добавляет товар в корзину."""
    customer_page.goto(f"{BASE_URL}/shop")
    customer_page.wait_for_selector("[data-testid='product-card']")

    initial_count = int(
        customer_page.locator("[data-testid='cart-count']").text_content() or "0"
    )

    customer_page.locator("[data-testid='product-card']").first.click()
    customer_page.click("[data-testid='add-to-cart-btn']")

    # Счётчик должен увеличиться
    customer_page.wait_for_function(
        f"() => parseInt(document.querySelector('[data-testid=cart-count]')?.textContent || '0') > {initial_count}"
    )
    customer_page.screenshot(path="tests/e2e/screenshots/05_add_to_cart.png")


def test_change_cart_quantity(customer_page: Page):
    """Изменение количества товара в корзине."""
    customer_page.goto(f"{BASE_URL}/cart")
    customer_page.wait_for_selector("[data-testid='cart-item']")

    # Увеличить количество
    customer_page.click("[data-testid='cart-qty-increase']")
    customer_page.wait_for_timeout(300)
    qty_text = customer_page.locator("[data-testid='cart-item-qty']").first.text_content()
    assert int(qty_text) >= 2

    # Уменьшить обратно
    customer_page.click("[data-testid='cart-qty-decrease']")
    customer_page.wait_for_timeout(300)
    qty_text = customer_page.locator("[data-testid='cart-item-qty']").first.text_content()
    assert int(qty_text) >= 1
    customer_page.screenshot(path="tests/e2e/screenshots/05_cart_qty.png")


def test_remove_from_cart(customer_page: Page):
    """Удаление товара из корзины — добавить второй и удалить его."""
    # Добавляем второй товар
    customer_page.goto(f"{BASE_URL}/shop")
    customer_page.wait_for_selector("[data-testid='product-card']")
    customer_page.locator("[data-testid='product-card']").nth(1).click()
    customer_page.click("[data-testid='add-to-cart-btn']")

    customer_page.goto(f"{BASE_URL}/cart")
    customer_page.wait_for_selector("[data-testid='cart-item']")
    item_count_before = customer_page.locator("[data-testid='cart-item']").count()

    # Удалить последний товар
    customer_page.locator("[data-testid='cart-remove-btn']").last.click()
    customer_page.wait_for_timeout(500)

    item_count_after = customer_page.locator("[data-testid='cart-item']").count()
    assert item_count_after == item_count_before - 1
    customer_page.screenshot(path="tests/e2e/screenshots/05_cart_removed.png")