## Status: DONE

## Completed:
- Переработана страница товара /products/[slug].vue — новая структура HERO + Description + Attributes
- HERO: grid 60/40 (desktop 768px+), stacked на mobile; галерея sticky top 80px
- Галерея: большое активное изображение с img-fade transition, горизонтальный скролл миниатюр, placeholder если нет изображений
- Buy Panel: sticky, категория-badge (ссылка), h1, цена (акцентный цвет, font-mono), stock badge (зелёный/жёлтый/серый с фоном), variant selector (кнопки-теги с border 2px accent при active), кнопка "В корзину" (loading state со спиннером), кнопка "Быстрый заказ", trust badges (гарантия/официальный товар/доставка)
- Description section: full width, max-width 800px, centered — TipTapViewer / description_html (с prose стилями) / plain text, font-size 1.1rem, line-height 1.8
- Attributes section: max-width 800px, таблица с чередующимися строками
- Sticky buy bar: появление снизу с transition, data-testid="sticky-buy-bar"
- Skeleton loader: повторяет структуру hero (60/40 grid), shimmer animation
- Error page: карточка с иконкой, кнопка "Вернуться в каталог"
- Исправлен баг в products/index.vue: AppBreadcrumbs получал :items вместо :crumbs
- Сохранена вся логика: addToCart (с loading state), selectedVariant, QuickBuyModal, SEO/Schema.org, handleScroll

## Artifacts:
- frontend/pages/products/[slug].vue (полная переработка)
- frontend/pages/products/index.vue (фикс пропа :crumbs)

## data-testid покрытие:
- product-gallery: галерея целиком
- product-gallery-main: основное изображение
- product-gallery-thumb: каждая миниатюра
- product-title: h1 заголовок
- product-price: цена
- product-stock: badge наличия
- product-variant-selector: контейнер вариантов
- add-to-cart-btn: кнопка В корзину
- btn-quick-buy: кнопка Быстрый заказ
- product-description: секция описания
- sticky-buy-bar: нижняя фиксированная панель

## Contracts Verified:
- data-testid на всех ключевых элементах: OK
- Только var(--color-*) токены, NO hex/rgb в .vue файле: OK
- Mobile-first breakpoints (320/480/768px): OK
- npm run lint (vue-tsc): OK — 0 ошибок
- npm run typecheck (vue-tsc): OK — 0 ошибок
- API shape совпадает с useProducts.ts (Product, ProductVariant, ProductImage): OK
- Именование IoTDevice / FirmwareDevice / accessToken: не используются в этом файле

## Next:
- testing-agent: e2e тесты для /products/[slug] — проверить gallery, variant selector, add-to-cart, sticky bar appearance

## Blockers:
- none
