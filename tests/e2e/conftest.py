import pytest
import os
import requests
from playwright.sync_api import Browser, BrowserContext, Page, expect

# --- Constants -----------------------------------------------------------------

BASE_URL = os.environ.get("BASE_URL", "http://localhost:3000")
API_URL = os.environ.get("API_URL", "http://localhost:8000")
ADMIN_EMAIL = "admin@wifiobd-test.ru"
ADMIN_PASS = "Admin123!"
CUSTOMER_EMAIL = "customer@wifiobd-test.ru"
CUSTOMER_PASS = "Customer123!"

# --- Helpers -------------------------------------------------------------------

def handle_console(msg):
    """Log browser console messages."""
    # Ignore noisy dev-server warnings
    if "ws" in msg.text or "vite" in msg.text:
        return
    print(f"BROWSER CONSOLE: [{msg.type}] {msg.text}")

def _login_via_api(email: str, password: str) -> str:
    """Логин через API, возвращает access_token."""
    resp = requests.post(f"{API_URL}/api/v1/auth/login", json={
        "email": email,
        "password": password,
    })
    assert resp.status_code == 200, f"Login failed for {email}: {resp.text}"
    return resp.json()["access_token"]


def _inject_token(page: Page, token: str) -> Page:
    """Устанавливает токен и перезагружает страницу."""
    page.goto(BASE_URL)
    page.evaluate(f"() => {{ localStorage.setItem('token', '{token}'); }}")
    page.reload()
    page.wait_for_load_state("networkidle")
    return page


def _make_context(browser: Browser) -> BrowserContext:
    context = browser.new_context(
        base_url=BASE_URL,
        viewport={"width": 1280, "height": 720}
    )
    context.set_default_navigation_timeout(15000)
    context.set_default_timeout(8000)
    return context

# --- Fixtures ------------------------------------------------------------------

@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    return {
        **browser_context_args,
        "base_url": BASE_URL,
        "viewport": {
            "width": 1280,
            "height": 720,
        },
    }

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
    pg.on("console", handle_console)
    _inject_token(pg, admin_token)
    # Убеждаемся что видим имя юзера (авторизация прошла)
    pg.wait_for_selector("[data-testid='user-name']", timeout=5000)
    return pg


@pytest.fixture
def customer_page(browser: Browser, customer_token: str):
    """Страница с авторизованным покупателем."""
    ctx = _make_context(browser)
    pg = ctx.new_page()
    pg.on("console", handle_console)
    _inject_token(pg, customer_token)
    pg.wait_for_selector("[data-testid='user-name']", timeout=5000)
    return pg

@pytest.fixture
def page(browser: Browser):
    with _make_context(browser) as context:
        pg = context.new_page()
        pg.on("console", handle_console)
        yield pg
