# tests/e2e/test_03_admin_products.py
from playwright.sync_api import Page, expect
from conftest import BASE_URL, fill_element, click_element
import re
import time

def test_admin_product_list(admin_page: Page):
    """Список товаров в админке загружается."""
    admin_page.goto(f"{BASE_URL}/admin/products")
    admin_page.wait_for_load_state("networkidle")
    
    # Ждем таблицу или карточки товаров
    admin_page.wait_for_selector("[data-testid='product-card'], table", timeout=15000)
    admin_page.screenshot(path="tests/e2e/screenshots/03_admin_products.png")

def test_admin_create_product(admin_page: Page):
    """Создание нового товара."""
    admin_page.goto(f"{BASE_URL}/admin/products/create")
    admin_page.wait_for_load_state("networkidle")
    
    # Генерируем уникальное название и слаг
    ts = int(time.time())
    name = f"E2E Новый OBD2 {ts}"
    
    # Селекторы из frontend/pages/admin/products/create.vue
    fill_element(admin_page, name, "admin-product-name")
    
    # Вводим слаг явно
    slug_input = admin_page.locator("input[placeholder='nazvanie-tovara']")
    if slug_input.is_visible():
        slug_input.fill(f"e2e-obd2-{ts}")
    
    fill_element(admin_page, "1500", "admin-product-price")
    fill_element(admin_page, "10", "admin-product-stock")
    
    # Сохраняем
    with admin_page.expect_navigation(timeout=15000):
        click_element(admin_page, "admin-save-btn")
    
    # Редирект идет на /admin/products/{id} (страницу редактирования)
    expect(admin_page).to_have_url(re.compile(r".*/admin/products/[0-9a-f-]+"))
    admin_page.screenshot(path="tests/e2e/screenshots/03_admin_product_created.png")

def test_admin_delete_product(admin_page: Page):
    """Удаление товара."""
    admin_page.goto(f"{BASE_URL}/admin/products")
    admin_page.wait_for_load_state("networkidle")
    
    # Ждем появления списка
    admin_page.wait_for_selector("[data-testid='admin-delete-btn']", timeout=10000)
    
    # Настраиваем обработку диалога подтверждения
    def handle_dialog(dialog):
        print(f"DIALOG: {dialog.message}")
        dialog.accept()
    
    admin_page.on("dialog", handle_dialog)
    
    # Нажимаем кнопку удаления у первого товара
    delete_btn = admin_page.locator("[data-testid='admin-delete-btn']").first
    delete_btn.click()
    
    # Ждем, пока список обновится (через networkidle или отсутствие лоадера)
    admin_page.wait_for_load_state("networkidle")
    admin_page.wait_for_timeout(1000) # Даем время на удаление в БД
    admin_page.screenshot(path="tests/e2e/screenshots/03_admin_product_deleted.png")
