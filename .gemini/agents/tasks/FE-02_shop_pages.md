---
id: FE-02
status: TODO
agent: frontend-agent
stage: Frontend shop
priority: HIGH
depends_on: [FE-01, BE-01, BE-03]
blocks: [FE-04]
---

# FE-02 — Страницы магазина (каталог, карточка, корзина, checkout)

## Цель

Реализовать публичные страницы магазина с SSR, SEO и интеграцией с API.

## ⚠️ Перед началом

```bash
list_directory frontend/pages/
list_directory frontend/components/shop/
```

## Страницы

### `/products` — Каталог
- SSR (`useAsyncData`), cursor pagination (кнопка «Ещё»)
- Фильтры по категории (query param `?category=slug`)
- `usePageSeo` с `title`, `description`
- Schema.org `BreadcrumbList`
- `canonical` без `sort` и `page`, но с `category`

### `/products/[slug]` — Карточка товара
- SSR, `useAsyncData`
- Schema.org `Product` + `Offer` + `AggregateRating` (если есть отзывы)
- `<img>` — `alt`, `width`, `height`, `loading="lazy"`, `srcset` 480w/800w/1200w
- Hero-изображение: `loading="eager" fetchpriority="high"`
- Кнопка «В корзину» → `cartStore.addItem()`
- Варианты (размер/цвет) — переключатель, меняет `variant_id` и цену
- Блок «В наличии» / «Нет в наличии» из stock

### `/cart` — Корзина
- CSR (нет смысла в SSR)
- Список из `cartStore`, изменение количества, удаление
- Итог: цена + предварительный расчёт доставки (CDEK)
- Кнопка «Оформить» → `/checkout`

### `/checkout` — Оформление
- Шаги: 1. Адрес + доставка, 2. Подтверждение, 3. Оплата
- ПВЗ СДЭК — выбор из списка `/api/v1/delivery/pickup-points`
- Создание заказа: POST `/api/v1/orders`
- Редирект на YooMoney `confirmation_url`

### `/orders/[id]` — Статус заказа
- SSR, live-обновление статуса через polling (каждые 30 сек)
- Прогресс-бар статусов: Создан → Оплачен → В обработке → Отправлен → Доставлен

## Компоненты (`frontend/components/shop/`)

Проверить наличие, создать отсутствующие:
- `ProductCard.vue` — name, price, image (lazy), кнопка в корзину
- `ProductGallery.vue` — зум, thumbnail-strip
- `CartItem.vue` — qty stepper, remove
- `CartSummary.vue` — total + delivery
- `OrderStatus.vue` — прогресс-бар
- `DeliveryPicker.vue` — список ПВЗ + карта (если есть)

## Контракты

- `useSeoMeta` и `canonical` — на каждой публичной странице
- `<img alt>` — обязательный атрибут, никогда пустой
- Stock-инфо — загружать отдельным запросом, не блокировать SSR
- Фильтры URL — только `?category=`, без других параметров в canonical

## Критерии готовности

- [ ] `/products` — SSR, SEO canonical, список с пагинацией
- [ ] `/products/[slug]` — Schema.org Product, srcset, variant switching
- [ ] `/cart` — добавление/удаление, пересчёт итога
- [ ] `/checkout` — создаёт заказ, редиректит на оплату
- [ ] `vue-tsc --noEmit` — 0 ошибок
- [ ] Lighthouse SEO ≥ 95 на `/products/[slug]`

## Отчёт

`.gemini/agents/reports/frontend/FE-02.md`
