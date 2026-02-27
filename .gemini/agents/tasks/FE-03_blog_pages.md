---
id: FE-03
status: TODO
agent: frontend-agent
stage: Frontend blog
priority: HIGH
depends_on: [FE-01, BE-02]
blocks: [FE-04]
---

# FE-03 — Страницы блога и TipTap-редактор

## Цель

Страницы блога с SSR/SEO + редактор TipTap в admin.

## ⚠️ Перед началом

```bash
list_directory frontend/pages/blog/
list_directory frontend/components/blog/
read_file frontend/package.json  # проверить наличие @tiptap/*
```

## Страницы

### `/blog` — Список статей
- SSR, cursor pagination
- Фильтры по категории и тегу
- Schema.org `BreadcrumbList`
- RSS ссылка в `<head>`: `<link rel="alternate" type="application/rss+xml">`

### `/blog/[slug]` — Статья
- SSR, `useAsyncData`
- Schema.org `BlogPosting` (datePublished, dateModified, author, image)
- `reading_time_minutes` — отображать «X мин чтения»
- Счётчик просмотров — не отображать (fire-and-forget на бэке)
- Форма комментария → POST `/api/v1/blog/posts/{id}/comments`
- `canonical` = `/blog/{slug}` без параметров

### `/admin/blog` — CRUD блога (только role=admin)
- Список постов с фильтром по статусу (draft/published/archived)
- Кнопки: создать, редактировать, удалить, предпросмотр

### `/admin/blog/[id]/edit` — Редактор
- TipTap editor с расширениями:
  ```json
  "@tiptap/vue-3", "@tiptap/starter-kit", "@tiptap/extension-image",
  "@tiptap/extension-youtube", "@tiptap/extension-link",
  "@tiptap/extension-placeholder", "@tiptap/extension-character-count",
  "@tiptap/extension-code-block-lowlight", "lowlight"
  ```
  Установить если нет в package.json
- SEO-панель: `meta_title` (счётчик символов, max 60), `meta_description` (max 160)
- Загрузка изображений: POST `/api/v1/media/upload` → TipTap `insertContent`
- Сохранение: отправляет `content_json` (не HTML)
- Статус: draft/published переключатель

## Компоненты (`frontend/components/blog/`)

- `PostCard.vue` — title, excerpt, date, reading_time, category
- `PostContent.vue` — рендерит `content_html` (v-html с DOMPurify на клиенте)
- `CommentForm.vue` — name, email (локально), body; success state
- `CommentList.vue` — список approved комментариев
- `TipTapEditor.vue` — основной редактор
- `SeoPanel.vue` — поля meta_title/description с счётчиком

## Контракты

- `v-html` — только с `content_html` из API, который уже прошёл `bleach.clean()` на бэке
- Дополнительно на клиенте: DOMPurify.sanitize() перед `v-html`
- `author_email` — НИКОГДА не отображать публично
- TipTap — сохранять `content_json`, HTML генерирует backend

## Критерии готовности

- [ ] `/blog/[slug]` — Schema.org BlogPosting в `<script type="application/ld+json">`
- [ ] Форма комментария — отправляет и показывает success state
- [ ] TipTap загружает существующий `content_json` при редактировании
- [ ] Загрузка изображения → вставляется в редактор
- [ ] SEO-панель считает символы meta_title в реальном времени
- [ ] `vue-tsc --noEmit` — 0 ошибок

## Отчёт

`.gemini/agents/reports/frontend/FE-03.md`
