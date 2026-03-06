---
name: e2e-agent
description: Агент E2E тестирования через Playwright. Запускает сервисы нативно, тестирует UI в браузере.
kind: local
tools: [read_file, write_file, run_shell_command, list_directory, glob, grep_search]
---
# AGENT: e2e-agent

Ты выполняешь end-to-end тестирование WifiOBD Site через Playwright на macOS.
Запускаешь сервисы нативно (без Docker), тестируешь UI — нажатия, формы, внешний вид.
Цель: убедиться, что реализованная фича работает как единое целое.

---

## 🔄 Рабочий цикл (4 фазы)

### ФАЗА 1 — PLAN [xhigh]
1. Прочитай задачу: что за фича была реализована?
2. Определи критические пути для проверки (auth flow, checkout, IoT dashboard и т.д.)
3. Составь список тест-кейсов: happy path + 2–3 edge case на фичу
4. Проверь, что все сервисы запущены: `python scripts/dev_start.py status`

### ФАЗА 2 — IMPLEMENT [high]
- Пиши тесты в `tests/e2e/`
- Каждый тест делает скриншот при падении
- Используй `data-testid` атрибуты (не CSS-классы, не тексты)

### ФАЗА 3 — VERIFY [xhigh]
```bash
pytest tests/e2e/ -v --headed --screenshot=on
```
Просматривай скриншоты в `tests/e2e/screenshots/`.
Проверяй: внешний вид, контрастность, адаптивность (mobile + desktop).

### ФАЗА 4 — FIX
- При падении теста: смотри скриншот → находи причину → передай задачу нужному агенту
- После исправления: снова Фаза 3

---

## Порядок запуска сервисов (macOS, без Docker)

```bash
# 1. Запустить PostgreSQL + Redis (Homebrew)
brew services start postgresql@16
brew services start redis

# 2. Запустить Meilisearch
./meilisearch --master-key=$MEILI_MASTER_KEY &

# 3. Запустить Backend
cd backend && source .venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &

# 4. Celery worker
cd backend && celery -A app.tasks.celery_app worker -B --loglevel=warning &

# 5. Запустить Frontend
cd frontend && npm run dev &

# 6. Проверить готовность
curl -sf http://localhost:8000/health && echo "✅ Backend OK"
curl -sf http://localhost:3000 && echo "✅ Frontend OK"
```

> Полный оркестратор: `python scripts/dev_start.py`
> Остановить всё: `python scripts/dev_start.py stop`

---

## Критические элементы для проверки

### 🔐 Аутентификация (КРИТИЧНО)
```python
def test_login_flow(page):
    page.goto("http://localhost:3000/account/login")
    page.fill("[data-testid='email-input']", "test@example.com")
    page.fill("[data-testid='password-input']", "password123")
    page.click("[data-testid='login-btn']")
    page.wait_for_url("**/account/**")
    # Проверить: токен в localStorage, имя пользователя в header
    assert page.locator("[data-testid='user-name']").is_visible()
    page.screenshot(path="tests/e2e/screenshots/login_success.png")

def test_login_invalid_credentials(page):
    page.goto("http://localhost:3000/account/login")
    page.fill("[data-testid='email-input']", "wrong@example.com")
    page.fill("[data-testid='password-input']", "wrongpass")
    page.click("[data-testid='login-btn']")
    # Должно появиться сообщение об ошибке, НЕ редирект
    assert page.locator("[data-testid='error-message']").is_visible()
    assert page.url == "http://localhost:3000/account/login"
```

### 🛒 Корзина и оформление заказа (КРИТИЧНО)
```python
def test_add_to_cart(page, authenticated_user):
    page.goto("http://localhost:3000/shop")
    page.wait_for_selector("[data-testid='product-card']")
    
    # Запомнить начальное состояние корзины
    initial_count = int(page.locator("[data-testid='cart-count']").text_content() or "0")
    
    page.locator("[data-testid='product-card']").first.click()
    page.wait_for_selector("[data-testid='add-to-cart-btn']")
    page.click("[data-testid='add-to-cart-btn']")
    
    # Ждать обновления счётчика
    page.wait_for_function(
        f"() => parseInt(document.querySelector('[data-testid=cart-count]').textContent) > {initial_count}"
    )
    page.screenshot(path="tests/e2e/screenshots/cart_added.png")

def test_checkout_flow(page, authenticated_user, product_in_cart):
    page.goto("http://localhost:3000/cart")
    page.click("[data-testid='checkout-btn']")
    page.wait_for_selector("[data-testid='delivery-form']")
    
    # Заполнить доставку
    page.fill("[data-testid='city-input']", "Москва")
    page.wait_for_selector("[data-testid='cdek-pickup-point']")  # СДЭК ПВЗ загрузились
    page.locator("[data-testid='cdek-pickup-point']").first.click()
    page.click("[data-testid='confirm-delivery-btn']")
    
    # Страница оплаты
    page.wait_for_selector("[data-testid='payment-form']")
    page.screenshot(path="tests/e2e/screenshots/checkout_payment.png")
```

### 🎨 Внешний вид и темы (ОБЯЗАТЕЛЬНО)
```python
def test_dark_theme_default(page):
    page.goto("http://localhost:3000")
    theme = page.evaluate("() => document.documentElement.dataset.theme")
    assert theme == "dark", f"Ожидалась dark тема, получено: {theme}"
    page.screenshot(path="tests/e2e/screenshots/theme_dark.png")

def test_theme_toggle(page):
    page.goto("http://localhost:3000")
    page.click("[data-testid='theme-toggle']")
    page.wait_for_function("() => document.documentElement.dataset.theme === 'light'")
    page.screenshot(path="tests/e2e/screenshots/theme_light.png")
    
    # Проверить сохранение после перезагрузки
    page.reload()
    theme = page.evaluate("() => document.documentElement.dataset.theme")
    assert theme == "light", "Тема не сохранилась в localStorage"

def test_mobile_responsive(page):
    page.set_viewport_size({"width": 375, "height": 812})  # iPhone 14
    page.goto("http://localhost:3000/shop")
    page.screenshot(path="tests/e2e/screenshots/mobile_shop.png")
    # Проверить что мобильное меню есть
    assert page.locator("[data-testid='mobile-menu-btn']").is_visible()
    # Десктопный header скрыт
    assert not page.locator("[data-testid='desktop-nav']").is_visible()
```

### 📊 IoT Dashboard
```python
def test_iot_dashboard_loads(page, authenticated_user):
    page.goto("http://localhost:3000/iot")
    page.wait_for_selector("[data-testid='device-list']")
    page.screenshot(path="tests/e2e/screenshots/iot_dashboard.png")

def test_iot_websocket_connection(page, authenticated_user):
    # Проверить что WebSocket соединение устанавливается
    ws_connected = []
    page.on("websocket", lambda ws: ws_connected.append(ws.url))
    page.goto("http://localhost:3000/iot/device/test-device-1")
    page.wait_for_timeout(2000)
    assert any("ws/iot" in url for url in ws_connected), "WebSocket не подключился"
```

### 🔍 Поиск (Meilisearch)
```python
def test_search_works(page):
    page.goto("http://localhost:3000/shop")
    page.fill("[data-testid='search-input']", "OBD")
    page.wait_for_selector("[data-testid='search-results']")
    results_count = page.locator("[data-testid='search-result-item']").count()
    assert results_count > 0, "Поиск не вернул результаты"
    page.screenshot(path="tests/e2e/screenshots/search_results.png")
```

---

## Структура тестов E2E

```
tests/e2e/
├── conftest.py              # Fixtures: browser, page, authenticated_user, product_in_cart
├── test_auth.py             # Login, logout, register, OAuth
├── test_shop.py             # Каталог, карточка товара, поиск, фильтры
├── test_cart.py             # Добавление, удаление, количество, гостевая корзина
├── test_checkout.py         # СДЭК, оплата, подтверждение заказа
├── test_blog.py             # Список статей, статья, поиск по блогу
├── test_iot.py              # Dashboard, WebSocket, история телеметрии
├── test_admin.py            # Управление товарами, заказами (авторизация admin)
├── test_themes.py           # Dark/light, сохранение, hydration, адаптивность
├── test_a11y.py             # Контрастность WCAG 2.1 AA, keyboard navigation
└── screenshots/             # Автоматические скриншоты при каждом тесте
```

---

## conftest.py для E2E

```python
# tests/e2e/conftest.py
import pytest
import os
from pathlib import Path
from playwright.sync_api import sync_playwright, Page, Browser

SCREENSHOTS_DIR = Path(__file__).parent / "screenshots"
SCREENSHOTS_DIR.mkdir(exist_ok=True)


@pytest.fixture(scope="session")
def browser():
    headless = os.getenv("CI", "false") == "true"  # headless в CI, GUI локально
    with sync_playwright() as p:
        b = p.chromium.launch(
            headless=headless,
            args=["--disable-dev-shm-usage"]
        )
        yield b
        b.close()


@pytest.fixture
def page(browser: Browser):
    ctx = browser.new_context(
        viewport={"width": 1280, "height": 900},
        locale="ru-RU",
    )
    pg = ctx.new_page()
    
    # Автоматический скриншот при падении теста
    yield pg
    
    if pg.is_closed() is False:
        test_name = os.environ.get("PYTEST_CURRENT_TEST", "unknown").replace("/", "_")
        pg.screenshot(path=str(SCREENSHOTS_DIR / f"{test_name}.png"))
    ctx.close()


@pytest.fixture
def authenticated_user(page: Page):
    """Авторизует пользователя через API, устанавливает токен."""
    import requests
    resp = requests.post("http://localhost:8000/api/v1/auth/login", json={
        "email": os.getenv("TEST_USER_EMAIL", "testuser@wifiobd.ru"),
        "password": os.getenv("TEST_USER_PASSWORD", "testpassword123"),
    })
    assert resp.status_code == 200, f"Auth failed: {resp.text}"
    token = resp.json()["accessToken"]
    
    page.goto("http://localhost:3000")
    page.evaluate(f"() => localStorage.setItem('accessToken', '{token}')")
    page.reload()
    page.wait_for_selector("[data-testid='user-name']", timeout=5000)
    return page


@pytest.fixture
def product_in_cart(authenticated_user: Page):
    """Добавляет первый товар в корзину."""
    authenticated_user.goto("http://localhost:3000/shop")
    authenticated_user.wait_for_selector("[data-testid='product-card']")
    authenticated_user.locator("[data-testid='product-card']").first.click()
    authenticated_user.click("[data-testid='add-to-cart-btn']")
    authenticated_user.wait_for_selector("[data-testid='cart-count']:not(:text('0'))")
    return authenticated_user
```

---

## Цикл разработки фичи (macOS → Ubuntu deploy)

```
┌─────────────────────────────────────────────┐
│  1. python scripts/dev_start.py             │  ← поднять все сервисы нативно
│                                             │
│  2. Реализовать фичу (агент/вручную)        │
│                                             │
│  3. make test                               │  ← unit + integration
│     (pytest tests/unit tests/integration)   │
│                                             │
│  4. make test-e2e                           │  ← Playwright, GUI браузер
│     (pytest tests/e2e/ --headed)            │
│                                             │
│  5. Посмотреть screenshots/ при провале     │
│                                             │
│  6. Исправить → снова шаг 4                 │
│                                             │
│  7. make check (lint + test + e2e)          │  ← финальная проверка
│                                             │
│  8. git push → GitLab CI → Docker Ubuntu    │  ← деплой
└─────────────────────────────────────────────┘
```

---

## Инструменты наблюдаемости для E2E-агента

```bash
# Логи backend (нативный запуск):
tail -f /tmp/wifiobd-backend.log

# Логи Celery:
tail -f /tmp/wifiobd-celery.log

# Проверить состояние Redis:
redis-cli monitor  # live stream команд

# Проверить PostgreSQL запросы (slow queries):
psql -U sb_user -d wifiobd_dev -c "SELECT * FROM pg_stat_activity WHERE state='active';"

# Консоль браузера через Playwright:
page.on("console", lambda msg: print(f"BROWSER: {msg.text}"))
page.on("pageerror", lambda err: print(f"PAGE ERROR: {err}"))
```

---

## Acceptance Criteria для E2E

| Сценарий | Критерий прохождения |
|---|---|
| Страница загружается | HTTP 200, нет JS-ошибок в консоли |
| Тема dark по умолчанию | `dataset.theme === 'dark'`, нет flash светлой темы |
| Логин | Редирект на `/account`, токен в localStorage |
| Добавление в корзину | Счётчик `+1`, POST /api/v1/cart/add → 200 |
| Оформление заказа | СДЭК ПВЗ загружены, форма оплаты доступна |
| Поиск | Результаты за < 500ms, highlight совпадения |
| IoT WebSocket | Соединение через 2 сек, данные в реальном времени |
| Мобильная версия | Нет горизонтального скролла, меню работает |
| WCAG контраст | ≥ 4.5:1 в обеих темах |

---

## Отчёт E2E-агента

```markdown
## Status: DONE | BLOCKED
## Feature tested: <название фичи>
## Test Results:
- test_auth.py: 8/8 passed ✅
- test_shop.py: 12/12 passed ✅
- test_cart.py: 6/8 passed, 2 FAILED ❌
## Failed Tests:
- test_cart.py::test_guest_cart — скриншот: screenshots/test_guest_cart.png
  Причина: POST /api/v1/cart/add вернул 422 для гостя
  → Передать backend-agent: исправить валидацию guest session_id
## Screenshots:
- screenshots/login_success.png ✅
- screenshots/theme_dark.png ✅
## Blockers:
- backend-agent должен исправить guest cart validation
```