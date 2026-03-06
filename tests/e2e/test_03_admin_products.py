# tests/e2e/test_03_admin_products.py
from playwright.sync_api import Page, expect
from conftest import BASE_URL

# Данные нового товара — создаётся здесь, используется в test_04_shop.py
NEW_PRODUCT_NAME = "E2E Тестовый товар"


def test_admin_sees_product_list(admin_page: Page):
    """Администратор видит список товаров."""
    admin_page.goto(f"{BASE_URL}/admin/products")
    admin_page.wait_for_selector("[data-testid='product-card'], table", timeout=8000)
    admin_page.screenshot(path="tests/e2e/screenshots/03_admin_product_list.png")


def test_admin_add_product(admin_page: Page):
    """Администратор добавляет новый товар."""
    admin_page.goto(f"{BASE_URL}/admin/products/new")
    admin_page.wait_for_selector("[data-testid='admin-product-form']")

    admin_page.fill("[data-testid='admin-product-name']", NEW_PRODUCT_NAME)
    admin_page.fill("[data-testid='admin-product-price']", "1490")
    admin_page.fill("[data-testid='admin-product-stock']", "25")
    admin_page.fill("[data-testid='admin-product-sku']", "E2E-TEST-002")

    admin_page.click("[data-testid='admin-save-btn']")

    # Редирект в список или страницу товара
    admin_page.wait_for_load_state("networkidle")
    admin_page.screenshot(path="tests/e2e/screenshots/03_admin_product_added.png")

    # Проверяем в каталоге
    admin_page.goto(f"{BASE_URL}/shop")
    admin_page.fill("[data-testid='search-input']", NEW_PRODUCT_NAME)
    admin_page.wait_for_selector("[data-testid='search-results']")
    expect(admin_page.locator(f"text={NEW_PRODUCT_NAME}")).to_be_visible()


def test_admin_delete_product(admin_page: Page):
    """Администратор удаляет товар 'Тестовый товар для удаления'."""
    admin_page.goto(f"{BASE_URL}/admin/products")
    admin_page.wait_for_selector("[data-testid='product-card']")

    # Найти товар по slug/имени
    admin_page.fill("[data-testid='search-input']", "Тестовый товар для удаления")
    admin_page.wait_for_timeout(500)

    delete_btn = admin_page.locator("[data-testid='admin-delete-btn']").first
    expect(delete_btn).to_be_visible()
    delete_btn.click()

    # Подтвердить удаление в диалоге
    admin_page.click("[data-testid='admin-confirm-delete']")
    admin_page.wait_for_load_state("networkidle")

    # Товара больше нет в списке
    admin_page.fill("[data-testid='search-input']", "Тестовый товар для удаления")
    admin_page.wait_for_timeout(500)
    count = admin_page.locator("text=Тестовый товар для удаления").count()
    assert count == 0, "Товар не был удалён"
    admin_page.screenshot(path="tests/e2e/screenshots/03_product_deleted.png")


def test_admin_manages_users(admin_page: Page):
    """Администратор видит список пользователей."""
    admin_page.goto(f"{BASE_URL}/admin/users")
    admin_page.wait_for_selector("[data-testid='user-row'], table", timeout=8000)
    # Проверяем что наш тестовый покупатель есть в списке
    expect(admin_page.locator("text=customer@wifiobd-test.ru")).to_be_visible()
    admin_page.screenshot(path="tests/e2e/screenshots/03_admin_users.png")