# tests/e2e/test_02_blog.py
from playwright.sync_api import Page, expect
from conftest import BASE_URL


def test_blog_list_loads(page: Page):
    """Список постов блога загружается."""
    page.goto(f"{BASE_URL}/blog")
    page.wait_for_selector("[data-testid='blog-post-card']", timeout=8000)
    count = page.locator("[data-testid='blog-post-card']").count()
    assert count >= 2, f"Ожидалось минимум 2 поста, получено: {count}"
    page.screenshot(path="tests/e2e/screenshots/02_blog_list.png")


def test_blog_post_opens(page: Page):
    """Открытие поста блога по клику."""
    page.goto(f"{BASE_URL}/blog")
    page.wait_for_selector("[data-testid='blog-post-card']")
    first_title = page.locator("[data-testid='blog-post-title']").first.text_content()
    page.locator("[data-testid='blog-post-card']").first.click()

    # Открылась страница поста
    page.wait_for_selector("[data-testid='blog-post-content']", timeout=5000)
    expect(page.locator("[data-testid='blog-post-content']")).to_be_visible()
    page.screenshot(path="tests/e2e/screenshots/02_blog_post.png")


def test_admin_create_blog_post(admin_page: Page):
    """Администратор создаёт новый пост в блоге."""
    admin_page.goto(f"{BASE_URL}/admin/blog/create")
    admin_page.wait_for_load_state("networkidle")
    
    admin_page.fill("[data-testid='admin-blog-title']", "E2E Тестовый пост")
    
    # Кликаем в редактор и печатаем
    editor = admin_page.locator("[data-testid='admin-blog-editor'] [contenteditable='true']")
    editor.click()
    editor.fill("Контент тестового поста для E2E")
    
    admin_page.click("[data-testid='admin-save-btn']", force=True)

    # После сохранения должен быть редирект в список админки
    admin_page.wait_for_url("**/admin/blog", timeout=10000)

    # Проверяем что пост появился в публичном списке
    admin_page.goto(f"{BASE_URL}/blog")
    admin_page.wait_for_selector("[data-testid='blog-post-card']", timeout=10000)
    titles = admin_page.locator("[data-testid='blog-post-title']").all_text_contents()
    assert any("E2E Тестовый пост" in t for u in titles for t in [u]) # titles is list of strings
    admin_page.screenshot(path="tests/e2e/screenshots/02_admin_blog_created.png")