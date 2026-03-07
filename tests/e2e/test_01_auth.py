# tests/e2e/test_01_auth.py
import pytest
from playwright.sync_api import Page, expect
import re
from conftest import BASE_URL, CUSTOMER_EMAIL, CUSTOMER_PASS, ADMIN_EMAIL, ADMIN_PASS, fill_element, click_element


def test_login_admin_success(page: Page):
    """Логин под администратором."""
    page.goto(f"{BASE_URL}/auth/login")
    page.wait_for_load_state("networkidle")

    fill_element(page, ADMIN_EMAIL, "email-input")
    fill_element(page, ADMIN_PASS, "password-input")

    # Клик с ожиданием навигации
    with page.expect_navigation(timeout=15000):
        click_element(page, "login-btn")

    # Проверяем, что залогинились
    page.wait_for_selector("[data-testid='user-name']", timeout=15000)
    expect(page.locator("[data-testid='user-name']")).to_be_visible()
    page.screenshot(path="tests/e2e/screenshots/01_admin_login.png")


def test_login_invalid_credentials(page: Page):
    """Неверные учётные данные — должна быть ошибка, не редирект."""
    page.goto(f"{BASE_URL}/auth/login")
    page.wait_for_load_state("networkidle")

    fill_element(page, "wrong@example.com", "email-input")
    fill_element(page, "wrongpassword", "password-input")
    click_element(page, "login-btn")

    expect(page.locator("[data-testid='auth-error']")).to_be_visible(timeout=10000)
    assert page.url.startswith(f"{BASE_URL}/auth/login")
    page.screenshot(path="tests/e2e/screenshots/01_login_error.png")


def test_register_new_user(page: Page):
    """Регистрация нового пользователя."""
    import time
    unique_email = f"newuser_{int(time.time())}@wifiobd-test.ru"

    page.goto(f"{BASE_URL}/auth/register")
    page.wait_for_load_state("networkidle")

    fill_element(page, "Иван Тестов", "name-input")
    fill_element(page, unique_email, "email-input")
    fill_element(page, "NewUser123!", "password-input")
    fill_element(page, "NewUser123!", "confirm-password-input")

    with page.expect_navigation(timeout=15000):
        click_element(page, "register-btn")

    # После регистрации — редирект на логин
    page.wait_for_url("**/auth/login", timeout=15000)
    page.screenshot(path="tests/e2e/screenshots/01_register_success.png")


def test_logout(customer_page: Page):
    """Выход из системы."""
    customer_page.goto(BASE_URL)
    customer_page.wait_for_load_state("networkidle")

    # Клик по кнопке выхода
    click_element(customer_page, "logout-btn")

    # После логаута кнопка "Войти" должна появиться
    expect(customer_page.locator("[data-testid='login-link']")).to_be_visible(timeout=10000)
    customer_page.screenshot(path="tests/e2e/screenshots/01_logout.png")