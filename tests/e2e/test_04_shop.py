# tests/e2e/test_04_shop.py
from playwright.sync_api import Page, expect
from conftest import BASE_URL, fill_element, click_element

def test_shop_page_loads(page: Page, test_product):
    """Страница каталога загружается и отображает товары."""
    page.goto(f"{BASE_URL}/products")
    page.wait_for_load_state("networkidle")
    
    # Ждем карточки товаров
    page.wait_for_selector("[data-testid='product-card']", timeout=15000)
    count = page.locator("[data-testid='product-card']").count()
    assert count >= 1, f"Ожидалось минимум 1 товар, получено: {count}"
    page.screenshot(path="tests/e2e/screenshots/04_shop_list.png")

def test_search_products(page: Page):
    """Поиск товаров на странице каталога."""
    page.goto(f"{BASE_URL}/products")
    page.wait_for_load_state("networkidle")
    
    # Ищем поле поиска
    search_input = page.locator("[data-testid='search-input'], input[placeholder*='Поиск']").first
    if search_input.is_visible():
        fill_element(page, "OBD2", "search-input", "input[placeholder*='Поиск']")
        # Даем время на фильтрацию (если она на фронте через computed или через API)
        page.wait_for_timeout(1000)
        
        # Проверяем наличие результатов
        count = page.locator("[data-testid='product-card']").count()
        assert count >= 1, "Поиск по 'OBD2' не дал результатов"
    page.screenshot(path="tests/e2e/screenshots/04_search.png")

def test_product_detail_page(page: Page, test_product):
    """Переход на детальную страницу товара."""
    page.goto(f"{BASE_URL}/products")
    page.wait_for_load_state("networkidle")
    
    # Кликаем по первой карточке товара
    first_product = page.locator("[data-testid='product-card']").first
    first_product.wait_for(state="visible", timeout=10000)
    
    # Кликаем по заголовку или всей карточке
    with page.expect_navigation(timeout=15000):
        first_product.click()
    
    # Проверяем элементы на странице товара
    page.wait_for_selector("[data-testid='add-to-cart-btn']", timeout=10000)
    expect(page.locator("[data-testid='product-price']")).to_be_visible()
    page.screenshot(path="tests/e2e/screenshots/04_product_detail.png")
