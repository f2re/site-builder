# tests/e2e/test_01_auth.py
import pytest
from playwright.sync_api import Page, expect
from conftest import BASE_URL, CUSTOMER_EMAIL, CUSTOMER_PASS, ADMIN_EMAIL, ADMIN_PASS


def test_login_admin_success(page: Page):
    """Логин под администратором."""
    page.goto(f"{BASE_URL}/auth/login")
    page.wait_for_load_state("networkidle")
    page.fill("[data-testid='email-input']", ADMIN_EMAIL)
    page.fill("[data-testid='password-input']", ADMIN_PASS)
    page.click("[data-testid='login-btn']", force=True)

    page.wait_for_selector("[data-testid='user-name']", timeout=15000)
    expect(page.locator("[data-testid='user-name']")).to_be_visible()
    page.screenshot(path="tests/e2e/screenshots/01_admin_login.png")


def test_login_invalid_credentials(page: Page):
    """Неверные учётные данные — должна быть ошибка, не редирект."""
    page.goto(f"{BASE_URL}/auth/login")
    page.wait_for_load_state("networkidle")
    page.fill("[data-testid='email-input']", "wrong@example.com")
    page.fill("[data-testid='password-input']", "wrongpassword")
    page.click("[data-testid='login-btn']", force=True)

    expect(page.locator("[data-testid='auth-error']")).to_be_visible(timeout=10000)
    assert page.url.startswith(f"{BASE_URL}/auth/login")
    page.screenshot(path="tests/e2e/screenshots/01_login_error.png")


def test_register_new_user(page: Page):
    """Регистрация нового пользователя."""
    import time
    unique_email = f"newuser_{int(time.time())}@wifiobd-test.ru"

    page.goto(f"{BASE_URL}/auth/register")
    page.wait_for_load_state("networkidle")
    page.fill("[data-testid='email-input']", unique_email)
    page.fill("[data-testid='password-input']", "NewUser123!")
    page.fill("[data-testid='confirm-password-input']", "NewUser123!")
    page.fill("[data-testid='name-input']", "Иван Тестов")
    page.click("[data-testid='register-btn']", force=True)

    # После регистрации — редирект на логин
    page.wait_for_url("**/auth/login", timeout=15000)
    page.screenshot(path="tests/e2e/screenshots/01_register_success.png")


def test_logout(customer_page: Page):
    """Выход из системы."""
    customer_page.goto(BASE_URL)
    customer_page.wait_for_load_state("networkidle")
    # На десктопе у нас кнопки в ряд, user-menu (профиль) не раскрывает меню
    # Нажимаем сразу logout-btn
    customer_page.click("[data-testid='logout-btn']", force=True)

    # После логаута кнопка "Войти" должна появиться
    expect(customer_page.locator("[data-testid='login-link']")).to_be_visible(timeout=10000)
    customer_page.screenshot(path="tests/e2e/screenshots/01_logout.png")