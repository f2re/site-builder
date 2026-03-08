@orchestrator Теперь у меня достаточно контекста. Вот полный план реализации:

***

## Анализ: iframe на mad-auto.ru

Страница wifiobd.ru (OpenCart) встраивает документацию с mad-auto.ru через `<iframe>`. Проблемы cross-origin iframe'ов с авторастяжением решаются через `postMessage` (если сайт-источник поддерживает `iframeResizer`) или через фиксированную высоту с `ResizeObserver`. Поскольку mad-auto.ru — внешний сайт без контроля над его кодом, применяем **комбинированный подход** .

***

## 1. Backend: модель + миграция + схема

### `backend/app/db/models/product.py` — добавить поле в `Product`

```python
# Добавить в класс Product:
doc_iframe_url: Mapped[Optional[str]] = mapped_column(
    String(2000), nullable=True, comment="URL для встраиваемого iframe документации (напр. mad-auto.ru)"
)
```

### Миграция `20260308_2000-d1e2f3a4b5c6_products_add_doc_iframe_url.py`

```python
"""products: add doc_iframe_url field

Revision ID: d1e2f3a4b5c6
Revises: a7f3b2c1d4e5
Create Date: 2026-03-08 20:00:00
"""
from alembic import op
import sqlalchemy as sa

revision = 'd1e2f3a4b5c6'
down_revision = 'a7f3b2c1d4e5'  # или актуальный head
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'products',
        sa.Column('doc_iframe_url', sa.String(2000), nullable=True,
                  comment='URL iframe документации (mad-auto.ru и др.)')
    )


def downgrade() -> None:
    op.drop_column('products', 'doc_iframe_url')
```

### Схема — добавить в `ProductDetailResponse`:

```python
doc_iframe_url: Optional[str] = None
```

***

## 2. Frontend: компонент `ProductDocIframe.vue`

Создать `frontend/components/shop/ProductDocIframe.vue` .

Ключевые технические решения:
- **`postMessage` listener** — mad-auto.ru может слать `{ type: 'resize', height: N }` или `{ iFrameHeight: N }` (формат `iframeResizer`)
- **`IntersectionObserver`** — загружаем iframe только когда он попадает в viewport (lazy)
- **`loading` оверлей** — показываем спиннер пока iframe не загрузился
- **CSP** — добавить `frame-src mad-auto.ru` в `nuxt.config.ts`

```vue
<!-- frontend/components/shop/ProductDocIframe.vue -->
<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'

const props = defineProps<{
  src: string
  title?: string
}>()

const iframeRef = ref<HTMLIFrameElement | null>(null)
const wrapperRef = ref<HTMLElement | null>(null)
const iframeHeight = ref(600)   // начальная высота (px)
const isLoaded = ref(false)
const isVisible = ref(false)    // lazy load

// ── Lazy load через IntersectionObserver ───────────────
let observer: IntersectionObserver | null = null

onMounted(() => {
  observer = new IntersectionObserver(
    (entries) => {
      if (entries[0].isIntersecting) {
        isVisible.value = true
        observer?.disconnect()
      }
    },
    { rootMargin: '200px' }  // предзагрузка за 200px до попадания в экран
  )
  if (wrapperRef.value) observer.observe(wrapperRef.value)

  // ── postMessage listener ───────────────────────────
  window.addEventListener('message', handleMessage)
})

onUnmounted(() => {
  observer?.disconnect()
  window.removeEventListener('message', handleMessage)
})

function handleMessage(event: MessageEvent) {
  // Безопасность: проверяем origin
  try {
    const url = new URL(props.src)
    if (event.origin !== url.origin) return
  } catch {
    return
  }

  const data = event.data

  // Поддержка разных форматов iframeResizer / кастомных
  let newHeight: number | null = null

  if (typeof data === 'object' && data !== null) {
    // iframeResizer формат: "[iFrameSizer]message:origin:height:..."
    if (typeof data === 'string' && (data as string).startsWith('[iFrameSizer]')) {
      const parts = (data as string).split(':')
      const h = parseInt(parts[2])
      if (!isNaN(h)) newHeight = h
    }
    // Кастомный формат от mad-auto.ru
    else if (data.type === 'resize' && typeof data.height === 'number') {
      newHeight = data.height
    } else if (data.type === 'setHeight' && typeof data.height === 'number') {
      newHeight = data.height
    } else if (typeof data.iFrameHeight === 'number') {
      newHeight = data.iFrameHeight
    } else if (typeof data.height === 'number') {
      newHeight = data.height
    }
  }
  // iframeResizer строковый формат
  if (typeof data === 'string' && data.startsWith('[iFrameSizer]')) {
    const parts = data.split(':')
    const h = parseInt(parts[2])
    if (!isNaN(h)) newHeight = h
  }

  if (newHeight && newHeight > 100) {
    iframeHeight.value = newHeight + 32  // небольшой запас
  }
}

function onIframeLoad() {
  isLoaded.value = true

  // Отправляем запрос высоты если iframeResizer поддерживается
  try {
    iframeRef.value?.contentWindow?.postMessage(
      { type: 'getHeight' },
      new URL(props.src).origin
    )
  } catch (_) {}
}
</script>

<template>
  <div ref="wrapperRef" class="doc-iframe-wrapper">
    <!-- Заголовок секции -->
    <h2 class="product-section-title">
      <Icon name="ph:book-open-text-bold" size="22" aria-hidden="true" />
      Документация
    </h2>

    <div
      class="doc-iframe-container"
      :style="{ height: iframeHeight + 'px' }"
    >
      <!-- Loading overlay -->
      <Transition name="fade">
        <div v-if="!isLoaded" class="doc-iframe-loading" aria-live="polite">
          <span class="doc-iframe-spinner" aria-hidden="true" />
          <span class="doc-iframe-loading__text">Загрузка документации…</span>
        </div>
      </Transition>

      <!-- iframe — рендерится только после IntersectionObserver -->
      <iframe
        v-if="isVisible"
        ref="iframeRef"
        :src="src"
        :title="title || 'Документация к товару'"
        class="doc-iframe"
        :class="{ 'doc-iframe--loaded': isLoaded }"
        loading="lazy"
        allowfullscreen
        referrerpolicy="strict-origin-when-cross-origin"
        sandbox="allow-scripts allow-same-origin allow-popups allow-forms"
        @load="onIframeLoad"
      />
    </div>

    <!-- Ссылка на внешний сайт (fallback / SEO) -->
    <a
      :href="src"
      target="_blank"
      rel="noopener noreferrer"
      class="doc-iframe-external-link"
      aria-label="Открыть документацию в новой вкладке"
    >
      <Icon name="ph:arrow-square-out-bold" size="14" />
      Открыть в новой вкладке
    </a>
  </div>
</template>

<style scoped>
.doc-iframe-wrapper {
  max-width: 100%;
  width: 100%;
}

.product-section-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: var(--text-xl);
  font-weight: 800;
  color: var(--color-text);
  margin: 0 0 24px;
  padding-left: 14px;
  border-left: 4px solid var(--color-accent);
}

.doc-iframe-container {
  position: relative;
  width: 100%;
  min-height: 400px;
  border-radius: var(--radius-xl);
  border: 1px solid var(--color-border);
  overflow: hidden;
  background: var(--color-surface);
  transition: height 0.3s ease;
}

.doc-iframe {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  border: none;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.doc-iframe--loaded {
  opacity: 1;
}

/* Loading state */
.doc-iframe-loading {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
  background: var(--color-surface);
  z-index: 1;
}

.doc-iframe-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid var(--color-border);
  border-top-color: var(--color-accent);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

.doc-iframe-loading__text {
  font-size: var(--text-sm);
  color: var(--color-muted);
}

/* External link */
.doc-iframe-external-link {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  margin-top: 12px;
  font-size: var(--text-xs);
  color: var(--color-muted);
  text-decoration: none;
  transition: color var(--transition-fast);
}

.doc-iframe-external-link:hover {
  color: var(--color-accent);
}

/* Fade transition */
.fade-leave-active { transition: opacity 0.3s ease; }
.fade-leave-to { opacity: 0; }
</style>
```

***

## 3. Использование в `pages/products/[slug].vue`

Добавить после секции `product-description` и перед `product-attributes` :

```vue
<!-- Импорт в <script setup> -->
import ProductDocIframe from '~/components/shop/ProductDocIframe.vue'

<!-- computed -->
const hasDocIframe = computed(() => !!product.value?.doc_iframe_url)

<!-- В <template>, после секции product-description: -->
<ProductDocIframe
  v-if="hasDocIframe"
  :src="product.doc_iframe_url!"
  :title="`Документация: ${product.name}`"
/>
```

***

## 4. Поле в админке `pages/admin/products/[id].vue`

В секции SEO/настроек добавить поле :

```vue
<!-- В форме редактирования товара -->
<div class="form-group">
  <label class="form-label" for="doc_iframe_url">
    <Icon name="ph:frame-corners-bold" size="16" />
    URL документации (iframe)
  </label>
  <input
    id="doc_iframe_url"
    v-model="form.doc_iframe_url"
    type="url"
    class="form-input"
    placeholder="https://mad-auto.ru/docs/wiobd..."
  />
  <p class="form-hint">
    Будет отображаться как встроенный фрейм после описания товара
  </p>
  <!-- Превью -->
  <a
    v-if="form.doc_iframe_url"
    :href="form.doc_iframe_url"
    target="_blank"
    rel="noopener"
    class="form-preview-link"
  >
    <Icon name="ph:eye-bold" size="14" />
    Предпросмотр в новой вкладке
  </a>
</div>
```

***

## 5. CSP в `nuxt.config.ts`

```ts
// frontend/nuxt.config.ts
routeRules: {
  '/products/**': {
    headers: {
      'Content-Security-Policy':
        "frame-src 'self' https://mad-auto.ru https://*.mad-auto.ru;"
    }
  }
}
```

***

## Сводка изменяемых файлов

| Файл | Изменение |
|------|-----------|
| `backend/app/db/models/product.py` | `doc_iframe_url: Optional[str]` |
| `backend/app/api/v1/products/schemas.py` | `doc_iframe_url` в `ProductDetailResponse` |
| `backend/app/db/migrations/versions/20260308_2000-…py` | Новая миграция Alembic |
| `frontend/components/shop/ProductDocIframe.vue` | **Новый компонент** с lazy-load + postMessage |
| `frontend/pages/products/[slug].vue` | Секция `<ProductDocIframe>` после описания |
| `frontend/pages/admin/products/[id].vue` | Поле `doc_iframe_url` в форме |
| `frontend/nuxt.config.ts` | CSP `frame-src mad-auto.ru` |
не забывай про mobile-first современный дизайн.
сам не пиши код, делегируй агентам. в конце запусти тесты и линты перед коммитом, закоммить изменения