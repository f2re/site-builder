## Status: DONE

## Completed:
- Установлен пакет `tiptap-markdown` (npm install --legacy-peer-deps)
- `Markdown` extension подключён в `TipTapEditor.vue` и `URichEditor.vue`
- Добавлены кнопки MD↑ (импорт) и MD↓ (экспорт) на тулбары обоих редакторов
- Реализованы inline-модалы для импорта Markdown (textarea + кнопка "Применить")
- Реализованы inline-модалы для экспорта Markdown (readonly textarea + кнопка "Копировать")
- Экспорт через `editor.storage.markdown.getMarkdown()`
- Импорт через `editor.commands.setContent(markdownString)`
- Копирование через `navigator.clipboard.writeText()`
- Кнопки MD окрашены в `var(--color-neon)` для визуального разграничения от обычных кнопок тулбара
- Все модалы используют только `var(--color-*)` токены
- Добавлены `data-testid` на все интерактивные элементы MD-функционала
- Добавлены `aria-label` на кнопки, `role="dialog"` + `aria-modal="true"` на оверлеи
- Mobile-first: на экранах < 640px модалы появляются снизу (bottom sheet)

## Artifacts:
- `/Users/meteo/Documents/WWW/site-builder/frontend/components/blog/TipTapEditor.vue`
- `/Users/meteo/Documents/WWW/site-builder/frontend/components/U/URichEditor.vue`

## Contracts Verified:
- data-testid на всех элементах: OK
  - `tiptap-import-md-btn`, `tiptap-export-md-btn`, `tiptap-import-md-modal`, `tiptap-export-md-modal`
  - `tiptap-md-input`, `tiptap-md-output`, `tiptap-apply-md-btn`, `tiptap-copy-md-btn`
  - `richeditor-import-md-btn`, `richeditor-export-md-btn`, `richeditor-import-md-modal`, `richeditor-export-md-modal`
  - `richeditor-md-input`, `richeditor-md-output`, `richeditor-apply-md-btn`, `richeditor-copy-md-btn`
- Только var(--color-*) токены: OK (нет hardcoded цветов)
- Mobile-first breakpoints: OK (max-width: 640px для bottom sheet)
- npm run lint: OK (0 ошибок)
- npm run typecheck: OK (0 ошибок)

## Accessibility:
- role="dialog" + aria-modal="true" на модалах
- aria-label на всех кнопках без текста
- Закрытие по клику на overlay (mousedown.self)

## Next:
- testing-agent: e2e тесты для MD-импорта/экспорта в TipTapEditor

## Blockers:
- none
