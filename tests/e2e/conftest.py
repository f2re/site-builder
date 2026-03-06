import os
import time
import requests
import pytest
from playwright.sync_api import Browser, BrowserContext, Page, Locator, expect

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
    if "ws" in msg.text or "vite" in msg.text:
        return
    print(f"BROWSER CONSOLE: [{msg.type}] {msg.text}")


def testid_selector(testid: str) -> str:
    return f"[data-testid='{testid}']"


def wait_for_any(page: Page, selectors: list[str], timeout: int = 8000) -> Locator:
    deadline = time.time() + timeout / 1000
    last_error = None

    while time.time() < deadline:
        for selector in selectors:
            locator = page.locator(selector).first
            try:
                locator.wait_for(state="visible", timeout=250)
                return locator
            except Exception as exc:
                last_error = exc
        page.wait_for_timeout(100)

    raise AssertionError(f"Could not find a visible element. Selectors tried: {selectors}. Last error: {last_error}")


def get_locator(page: Page, testid: str, *fallbacks: str, timeout: int = 8000) -> Locator:
    selectors = [testid_selector(testid), *fallbacks]
    return wait_for_any(page, selectors, timeout=timeout)


def goto_and_wait(page: Page, path: str, *, ready_testid: str | None = None, ready_selectors: list[str] | None = None) -> Page:
    url = f"{BASE_URL}{path}" if path.startswith("/") else path
    page.goto(url)
    page.wait_for_load_state("domcontentloaded")

    selectors = []
    if ready_testid:
        selectors.append(testid_selector(ready_testid))
    selectors.extend(ready_selectors or [])

    if selectors:
        wait_for_any(page, selectors)

    return page


def click_element(page: Page, testid: str, *fallbacks: str, timeout: int = 8000) -> Locator:
    locator = get_locator(page, testid, *fallbacks, timeout=timeout)
    locator.scroll_into_view_if_needed()
    expect(locator).to_be_visible(timeout=timeout)
    expect(locator).to_be_enabled(timeout=timeout)
    locator.click()
    return locator


def fill_element(page: Page, value: str, testid: str, *fallbacks: str, timeout: int = 8000) -> Locator:
    locator = get_locator(page, testid, *fallbacks, timeout=timeout)
    locator.scroll_into_view_if_needed()
    expect(locator).to_be_visible(timeout=timeout)
    expect(locator).to_be_enabled(timeout=timeout)
    locator.fill(value)
    return locator


def _login_via_api(email: str, password: str) -> str:
    """Логин через API, возвращает access_token."""
    resp = requests.post(
        f"{API_URL}/api/v1/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )
    assert resp.status_code == 200, f"Login failed for {email}: {resp.text}"
    return resp.json()["access_token"]


def _inject_token(page: Page, token: str) -> Page:
    """Устанавливает токен в куки и перезагружает страницу."""
    page.context.add_cookies([
        {
            "name": "access_token",
            "value": token,
            "domain": "localhost",
            "path": "/",
        }
    ])
    page.goto(BASE_URL)
    page.wait_for_load_state("networkidle")
    return page


def _make_context(browser: Browser) -> BrowserContext:
    context = browser.new_context(base_url=BASE_URL, viewport={"width": 1280, "height": 720})
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
    pg.wait_for_selector(testid_selector("user-name"), timeout=5000)
    return pg


@pytest.fixture
def customer_page(browser: Browser, customer_token: str):
    """Страница с авторизованным покупателем."""
    ctx = _make_context(browser)
    pg = ctx.new_page()
    pg.on("console", handle_console)
    _inject_token(pg, customer_token)
    pg.wait_for_selector(testid_selector("user-name"), timeout=5000)
    return pg


@pytest.fixture
def page(browser: Browser):
    with _make_context(browser) as context:
        pg = context.new_page()
        pg.on("console", handle_console)
        yield pg
