# tests/e2e/test_02_blog.py
from playwright.sync_api import Page, expect
from conftest import BASE_URL, fill_element, click_element
import re
import time

def test_blog_list_loads(page: Page):
    """Список постов блога загружается."""
    page.goto(f"{BASE_URL}/blog")
    page.wait_for_load_state("networkidle")
    
    # Ждем карточки постов
    page.wait_for_selector("[data-testid='blog-post-card']", timeout=15000)
    count = page.locator("[data-testid='blog-post-card']").count()
    assert count >= 1, f"Ожидался минимум 1 пост, получено: {count}"
    page.screenshot(path="tests/e2e/screenshots/02_blog_list.png")

def test_blog_post_opens(page: Page):
    """Открытие поста блога."""
    page.goto(f"{BASE_URL}/blog")
    page.wait_for_load_state("networkidle")
    
    first_post = page.locator("[data-testid='blog-post-card']").first
    first_post.wait_for(state="visible", timeout=10000)
    
    # Кликаем по ссылке или заголовку внутри карточки
    with page.expect_navigation(timeout=15000):
        first_post.click()
    
    # Проверяем наличие заголовка и контента
    expect(page.locator("[data-testid='blog-post-title']")).to_be_visible(timeout=15000)
    expect(page.locator("[data-testid='blog-post-content']")).to_be_visible(timeout=15000)
    page.screenshot(path="tests/e2e/screenshots/02_blog_post.png")

def test_admin_create_blog_post(admin_page: Page):
    """Администратор создаёт новый пост в блоге."""
    admin_page.goto(f"{BASE_URL}/admin/blog/create")
    admin_page.wait_for_load_state("networkidle")

    # Генерируем уникальное название и слаг
    ts = int(time.time())
    title = f"E2E Пост {ts}"
    
    fill_element(admin_page, title, "admin-blog-title")
    
    # Ждем автогенерации слага или вводим вручную для надежности
    slug_input = admin_page.locator("input[placeholder='auto-generated-from-title']")
    expect(slug_input).to_be_visible()
    fill_element(admin_page, f"e2e-post-{ts}", "admin-blog-slug", "input[placeholder='auto-generated-from-title']")
    
    # Работа с TipTap редактором
    editor = admin_page.locator(".ProseMirror").first
    editor.wait_for(state="visible", timeout=10000)
    editor.click()
    editor.fill(f"Это тестовый контент {ts}, созданный в рамках E2E теста.")
    
    # Нажимаем сохранить
    with admin_page.expect_navigation(timeout=15000):
        click_element(admin_page, "admin-save-btn")
    
    # Ждем редиректа на список или страницу редактирования (зависит от логики фронта)
    # Судя по коду фронта: router.push('/admin/blog')
    admin_page.wait_for_url("**/admin/blog", timeout=15000)
    expect(admin_page).to_have_url(re.compile(r".*/admin/blog$"))
    admin_page.screenshot(path="tests/e2e/screenshots/02_admin_blog_created.png")
