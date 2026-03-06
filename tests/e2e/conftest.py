# tests/e2e/conftest.py
import pytest
import requests
import os
from pathlib import Path
from playwright.sync_api import sync_playwright, Page, Browser, BrowserContext

BASE_URL = os.getenv("E2E_BASE_URL", "http://localhost:3000")
API_URL = os.getenv("E2E_API_URL", "http://localhost:8000")
SCREENSHOTS = Path(__file__).parent / "screenshots"
SCREENSHOTS.mkdir(exist_ok=True)

# Тестовые аккаунты (создаются seed_e2e.py)
ADMIN_EMAIL = "admin@wifiobd-test.ru"
ADMIN_PASS = "Admin123!"
CUSTOMER_EMAIL = "customer@wifiobd-test.ru"
CUSTOMER_PASS = "Customer123!"


@pytest.fixture(scope="session")
def browser():
    headless = os.getenv("CI", "false") == "true"
    with sync_playwright() as p:
        b = p.chromium.launch(
            headless=headless,
            slow_mo=50 if not headless else 0,  # замедление для визуального наблюдения
        )
        yield b
        b.close()


def _make_context(browser: Browser, **kwargs) -> BrowserContext:
    return browser.new_context(
        viewport={"width": 1280, "height": 900},
        locale="ru-RU",
        # Перехватываем console errors
        **kwargs
    )


def _login_via_api(email: str, password: str) -> str:
    """Логин через API, возвращает accessToken."""
    resp = requests.post(f"{API_URL}/api/v1/auth/login", json={
        "email": email,
        "password": password,
    })
    assert resp.status_code == 200, f"Login failed for {email}: {resp.text}"
    return resp.json()["accessToken"]


def _inject_token(page: Page, token: str) -> Page:
    """Устанавливает токен и перезагружает страницу."""
    page.goto(BASE_URL)
    page.evaluate(f"() => localStorage.setItem('accessToken', '{token}')")
    page.reload()
    page.wait_for_load_state("networkidle")
    return page


@pytest.fixture
def page(browser: Browser):
    """Чистая страница без авторизации."""
    ctx = _make_context(browser)
    pg = ctx.new_page()

    # Перехват JS ошибок
    js_errors = []
    pg.on("pageerror", lambda err: js_errors.append(str(err)))

    yield pg

    # Скриншот при падении
    if pg.is_closed() is False:
        test_name = os.environ.get("PYTEST_CURRENT_TEST", "unknown").split("::")[-1]
        pg.screenshot(path=str(SCREENSHOTS / f"{test_name}.png"))

    ctx.close()

    # Проверяем JS ошибки после теста
    critical = [e for e in js_errors if "TypeError" in e or "ReferenceError" in e]
    if critical:
        pytest.fail(f"JS ошибки на странице: {critical}")


@pytest.fixture(scope="session")
def admin_token():
    return _login_via_api(ADMIN_EMAIL, ADMIN_PASS)


@pytest.fixture(scope="session")
def customer_token():
    return _login_via_api(CUSTOMER_EMAIL, CUSTOMER_PASS)


@pytest.fixture
def admin_page(browser: Browser, admin_token: str):
    """Страница с авторизованным администратором."""
    ctx = _make_context(browser)
    pg = ctx.new_page()
    _inject_token(pg, admin_token)
    # Убеждаемся что видим имя юзера (авторизация прошла)
    pg.wait_for_selector("[data-testid='user-name']", timeout=5000)
    yield pg
    ctx.close()


@pytest.fixture
def customer_page(browser: Browser, customer_token: str):
    """Страница с авторизованным покупателем."""
    ctx = _make_context(browser)
    pg = ctx.new_page()
    _inject_token(pg, customer_token)
    pg.wait_for_selector("[data-testid='user-name']", timeout=5000)
    yield pg
    ctx.close()


# ── Mock для внешних сервисов ─────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def mock_cdek_api(page: Page):
    """Перехватываем CDEK API calls на уровне браузера — отдаём фиктивные ПВЗ."""
    def handle_cdek(route):
        if "/cdek" in route.request.url or "cdek.ru" in route.request.url:
            route.fulfill(
                status=200,
                content_type="application/json",
                body='{"entity":{"pickup_points":[{"code":"MSK001","name":"ПВЗ Москва Центр","address":"ул. Тверская, 1"}]}}'
            )
        else:
            route.continue_()
    page.route("**/*", handle_cdek)