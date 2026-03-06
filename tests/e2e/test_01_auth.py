# tests/e2e/test_01_auth.py
import pytest
from playwright.sync_api import Page, expect
from conftest import BASE_URL, CUSTOMER_EMAIL, CUSTOMER_PASS, ADMIN_EMAIL, ADMIN_PASS


def test_login_admin_success(page: Page):
    """Логин под администратором."""
    page.goto(f"{BASE_URL}/auth/login")
    page.fill("[data-testid='email-input']", ADMIN_EMAIL)
    page.fill("[data-testid='password-input']", ADMIN_PASS)
    page.click("[data-testid='login-btn']")

    page.wait_for_selector("[data-testid='user-name']", timeout=8000)
    expect(page.locator("[data-testid='user-name']")).to_be_visible()
    page.screenshot(path="tests/e2e/screenshots/01_admin_login.png")


def test_login_invalid_credentials(page: Page):
    """Неверные учётные данные — должна быть ошибка, не редирект."""
    page.goto(f"{BASE_URL}/auth/login")
    page.fill("[data-testid='email-input']", "wrong@example.com")
    page.fill("[data-testid='password-input']", "wrongpassword")
    page.click("[data-testid='login-btn']")

    expect(page.locator("[data-testid='auth-error']")).to_be_visible()
    assert page.url == f"{BASE_URL}/auth/login"
    page.screenshot(path="tests/e2e/screenshots/01_login_error.png")


def test_register_new_user(page: Page):
    """Регистрация нового пользователя."""
    import time
    unique_email = f"newuser_{int(time.time())}@wifiobd-test.ru"

    page.goto(f"{BASE_URL}/auth/register")
    page.fill("[data-testid='email-input']", unique_email)
    page.fill("[data-testid='password-input']", "NewUser123!")
    page.fill("[data-testid='name-input']", "Иван Тестов")
    page.click("[data-testid='register-btn']")

    # После регистрации — редирект или сообщение об успехе
    page.wait_for_selector("[data-testid='user-name'], [data-testid='register-success']", timeout=8000)
    page.screenshot(path="tests/e2e/screenshots/01_register_success.png")


def test_logout(customer_page: Page):
    """Выход из системы."""
    customer_page.goto(BASE_URL)
    customer_page.click("[data-testid='user-menu']")
    customer_page.click("[data-testid='logout-btn']")

    # После логаута кнопка "Войти" должна появиться
    expect(customer_page.locator("[data-testid='login-btn'], a[href*='login']")).to_be_visible(timeout=5000)
    page.screenshot(path="tests/e2e/screenshots/01_logout.png")