# tests/e2e/test_03_admin_products.py
from playwright.sync_api import Page, expect
from conftest import (
    BASE_URL,
    click_element,
    fill_element,
    goto_and_wait,
    wait_for_any,
)

# Данные нового товара — создаётся здесь, используется в test_04_shop.py
NEW_PRODUCT_NAME = "E2E Тестовый товар"


def test_admin_sees_product_list(admin_page: Page):
    """Администратор видит список товаров."""
    goto_and_wait(
        admin_page,
        "/admin/products",
        ready_selectors=["[data-testid='product-card']", "table"],
    )
    admin_page.screenshot(path="tests/e2e/screenshots/03_admin_product_list.png")


def test_admin_add_product(admin_page: Page):
    """Администратор добавляет новый товар."""
    goto_and_wait(
        admin_page,
        "/admin/products/new",
        ready_selectors=["[data-testid='admin-product-form']", "form"],
    )

    fill_element(
        admin_page,
        NEW_PRODUCT_NAME,
        "admin-product-name",
        "input[name='name']",
        "input[placeholder*='Название']",
        "input[placeholder*='название']",
    )
    fill_element(
        admin_page,
        "1490",
        "admin-product-price",
        "input[name='price']",
        "input[data-testid='price']",
    )
    fill_element(
        admin_page,
        "25",
        "admin-product-stock",
        "input[name='stock_quantity']",
        "input[data-testid='stock_quantity']",
    )
    fill_element(
        admin_page,
        "E2E-TEST-002",
        "admin-product-sku",
        "input[name='sku']",
        "input[placeholder*='SKU']",
    )

    click_element(admin_page, "admin-save-btn", "button[type='submit']")
    admin_page.wait_for_load_state("networkidle")
    admin_page.screenshot(path="tests/e2e/screenshots/03_admin_product_added.png")

    admin_page.goto(f"{BASE_URL}/shop")
    fill_element(
        admin_page,
        NEW_PRODUCT_NAME,
        "search-input",
        "input[type='search']",
        "input[placeholder*='Поиск']",
        "input[placeholder*='Search']",
    )
    wait_for_any(admin_page, ["[data-testid='search-results']", f"text={NEW_PRODUCT_NAME}"])
    expect(admin_page.locator(f"text={NEW_PRODUCT_NAME}").first).to_be_visible()


def test_admin_delete_product(admin_page: Page):
    """Администратор удаляет товар 'Тестовый товар для удаления'."""
    goto_and_wait(
        admin_page,
        "/admin/products",
        ready_selectors=["[data-testid='product-card']", "table"],
    )

    fill_element(
        admin_page,
        "Тестовый товар для удаления",
        "search-input",
        "input[type='search']",
        "input[placeholder*='Поиск']",
        "input[placeholder*='Search']",
    )
    admin_page.wait_for_load_state("networkidle")

    dialog_handled = []

    def _accept_dialog(dialog):
        dialog_handled.append(True)
        dialog.accept()

    admin_page.on("dialog", _accept_dialog)
    try:
        click_element(
            admin_page,
            "admin-delete-btn",
            "button[title='Удалить']",
            "button[aria-label='Удалить']",
        )
    finally:
        admin_page.remove_listener("dialog", _accept_dialog)

    if not dialog_handled:
        click_element(
            admin_page,
            "admin-confirm-delete",
            "button:has-text('Удалить')",
            "button:has-text('Подтвердить')",
        )

    admin_page.wait_for_load_state("networkidle")
    fill_element(
        admin_page,
        "Тестовый товар для удаления",
        "search-input",
        "input[type='search']",
        "input[placeholder*='Поиск']",
        "input[placeholder*='Search']",
    )
    admin_page.wait_for_load_state("networkidle")
    expect(admin_page.locator("text=Тестовый товар для удаления")).to_have_count(0)
    admin_page.screenshot(path="tests/e2e/screenshots/03_product_deleted.png")


def test_admin_manages_users(admin_page: Page):
    """Администратор видит список пользователей."""
    goto_and_wait(
        admin_page,
        "/admin/users",
        ready_selectors=["[data-testid='user-row']", "table"],
    )
    expect(admin_page.locator("text=customer@wifiobd-test.ru")).to_be_visible()
    admin_page.screenshot(path="tests/e2e/screenshots/03_admin_users.png")
