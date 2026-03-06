# E2E Testid Contract — WifiOBD Site

## Contract Version: 1.0
## Status: ACTIVE
## Owner: frontend-agent
## Consumers: testing-agent (e2e tests)
## Updated: 2026-03-06

> Канонический реестр всех `data-testid` атрибутов, требуемых E2E-тестами.
> frontend-agent ОБЯЗАН расставить все testid из этого файла.
> Добавлять новые testid только через этот контракт.
> Тесты используют ТОЛЬКО `[data-testid='...']` — никаких CSS-классов, XPath, text-selectors.

---

## Реестр data-testid

### Layout / Навигация (все страницы)

| testid | Элемент | Где |
|---|---|---|
| `header` | Тег `<header>` или блок навигации | `components/layout/AppHeader.vue` |
| `theme-toggle` | Кнопка переключения темы | `components/U/UThemeToggle.vue` |
| `cart-icon` | Иконка корзины в навбаре | `AppHeader.vue` |
| `cart-count` | Счётчик товаров в корзине (число) | `AppHeader.vue` |
| `user-menu` | Дропдаун-меню авторизованного юзера | `AppHeader.vue` |
| `user-name` | Имя/email авторизованного юзера | `AppHeader.vue` |
| `logout-btn` | Кнопка выхода внутри user-menu | `AppHeader.vue` |
| `mobile-menu-btn` | Бургер-кнопка мобильного меню | `AppHeader.vue` |

### Аутентификация (`/account/login`, `/account/register`)

| testid | Элемент | Где |
|---|---|---|
| `email-input` | Поле email | `pages/account/login.vue`, `pages/account/register.vue` |
| `password-input` | Поле пароля | `pages/account/login.vue`, `pages/account/register.vue` |
| `login-btn` | Кнопка "Войти" | `pages/account/login.vue` |
| `register-btn` | Кнопка "Зарегистрироваться" | `pages/account/register.vue` |
| `first-name-input` | Поле имени | `pages/account/register.vue` |
| `last-name-input` | Поле фамилии | `pages/account/register.vue` |
| `auth-error` | Блок с сообщением об ошибке | `pages/account/login.vue` |
| `register-success` | Сообщение об успешной регистрации | `pages/account/register.vue` |

### Магазин (`/shop`, `/shop/[slug]`)

| testid | Элемент | Где |
|---|---|---|
| `product-card` | Карточка товара в сетке | `components/shop/ProductCard.vue` |
| `product-title` | Название товара в карточке | `components/shop/ProductCard.vue` |
| `product-price` | Цена товара | `components/shop/ProductCard.vue`, `pages/shop/[slug].vue` |
| `product-stock` | Остаток / статус наличия | `pages/shop/[slug].vue` |
| `add-to-cart-btn` | Кнопка "В корзину" | `pages/shop/[slug].vue` |
| `search-input` | Поле поиска по товарам | `pages/shop/index.vue` (и `/admin/products`) |
| `search-results` | Контейнер с результатами поиска | `pages/shop/index.vue` |

### Корзина (`/cart`)

| testid | Элемент | Где |
|---|---|---|
| `cart-item` | Строка товара в корзине | `pages/cart.vue` |
| `cart-item-qty` | Текущее количество товара | `pages/cart.vue` |
| `cart-qty-increase` | Кнопка "+" | `pages/cart.vue` |
| `cart-qty-decrease` | Кнопка "-" | `pages/cart.vue` |
| `cart-remove-btn` | Кнопка удаления товара | `pages/cart.vue` |
| `cart-total` | Итоговая сумма | `pages/cart.vue` |
| `checkout-btn` | Кнопка "Оформить заказ" | `pages/cart.vue` |

### Оформление заказа (`/checkout`)

| testid | Элемент | Где |
|---|---|---|
| `delivery-form` | Форма выбора доставки | `pages/checkout.vue` |
| `city-input` | Поле ввода города | `pages/checkout.vue` |
| `cdek-pickup-point` | Элемент ПВЗ СДЭК в списке | `pages/checkout.vue` |
| `confirm-delivery-btn` | Кнопка подтверждения доставки | `pages/checkout.vue` |
| `payment-form` | Форма оплаты | `pages/checkout.vue` |
| `pay-btn` | Кнопка "Оплатить" | `pages/checkout.vue` |

### Заказы (`/account/orders`, `/account/orders/[id]`)

| testid | Элемент | Где |
|---|---|---|
| `order-list` | Контейнер списка заказов | `pages/account/orders.vue` |
| `order-card` | Карточка отдельного заказа | `pages/account/orders.vue`, `components/shop/OrderCard.vue` |
| `order-number` | Номер заказа | `components/shop/OrderCard.vue` |
| `order-status` | Статус заказа (badge/текст) | `components/shop/OrderCard.vue` |
| `order-items` | Список товаров в заказе | `pages/account/orders/[id].vue` |

### Блог (`/blog`, `/blog/[slug]`)

| testid | Элемент | Где |
|---|---|---|
| `blog-post-card` | Карточка поста в списке | `components/blog/BlogPostCard.vue` |
| `blog-post-title` | Заголовок поста в карточке | `components/blog/BlogPostCard.vue` |
| `blog-post-content` | Контент открытого поста | `pages/blog/[slug].vue` |

### Админ-панель (`/admin/*`)

| testid | Элемент | Где |
|---|---|---|
| `admin-product-form` | Форма создания/редактирования товара | `pages/admin/products/new.vue`, `pages/admin/products/[id].vue` |
| `admin-product-name` | Поле названия товара | `pages/admin/products/new.vue` |
| `admin-product-price` | Поле цены товара | `pages/admin/products/new.vue` |
| `admin-product-stock` | Поле количества на складе | `pages/admin/products/new.vue` |
| `admin-product-sku` | Поле SKU | `pages/admin/products/new.vue` |
| `admin-blog-form` | Форма создания/редактирования поста | `pages/admin/blog/new.vue` |
| `admin-blog-title` | Поле заголовка поста | `pages/admin/blog/new.vue` |
| `admin-blog-content` | Поле контента поста | `pages/admin/blog/new.vue` |
| `admin-save-btn` | Кнопка "Сохранить" | Все admin-формы |
| `admin-delete-btn` | Кнопка "Удалить" в списке | `pages/admin/products/index.vue` |
| `admin-confirm-delete` | Кнопка подтверждения удаления | Модальный диалог |
| `user-row` | Строка пользователя в таблице | `pages/admin/users.vue` |

---

## Правила расстановки

1. `data-testid` ставится непосредственно на интерактивный элемент (`<button>`, `<input>`, `<a>`).
2. На контейнер-обёртку (`product-card`, `cart-item`, `order-card`) — на корневой `<div>` компонента.
3. Значение testid — kebab-case, никаких пробелов и спецсимволов.
4. Один элемент — один testid. Не дублировать на родителе и дочернем.
5. В списках testid одинаков у всех однотипных элементов (Playwright использует `.first()`, `.nth()`, `.count()`).

---

## Проверка покрытия (выполняется testing-agent перед запуском E2E)

```bash
# Проверить наличие всех обязательных testid в исходниках frontend
grep -r "data-testid=" frontend/components frontend/pages \
  | grep -oP 'data-testid="[^"]+"' \
  | sort -u
```

Вывод должен содержать ВСЕ testid из таблиц выше.
