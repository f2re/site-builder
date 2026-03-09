## Status: DONE

## Completed:
- Fixed `content_json` loading in blog post editor — fallback to `content_html` when `content_json` is empty object or null
- Fixed `content_json` loading in product editor — fallback to `description_html` when `content_json` is empty
- Fixed TipTap editor `watch()` to handle both HTML strings and JSON objects without corrupting content via `JSON.stringify` comparison
- Added HTML import button (HTML↑) to TipTap editor toolbar with full modal UI
- Verified `TipTapViewer.vue` already handles both HTML strings and JSON via `setContent()` natively — no functional change needed, added explanatory comment

## Artifacts:
- /Users/meteo/Documents/WWW/site-builder/frontend/pages/admin/blog/[slug].vue
- /Users/meteo/Documents/WWW/site-builder/frontend/pages/admin/products/[id].vue
- /Users/meteo/Documents/WWW/site-builder/frontend/components/blog/TipTapEditor.vue
- /Users/meteo/Documents/WWW/site-builder/frontend/components/blog/TipTapViewer.vue

## Key Changes:

### blog/[slug].vue (line ~61)
```js
const hasJson = post.value.content_json && Object.keys(post.value.content_json).length > 0
form.content_json = hasJson ? post.value.content_json : (post.value.content_html || null)
```

### products/[id].vue (watch callback)
```js
const hasJson = newVal.content_json && Object.keys(newVal.content_json).length > 0
const contentFallback = hasJson ? newVal.content_json : (newVal.description_html || null)
// content_json: contentFallback
```
Note: `Product` type has `description_html` but no `content_html` — only `description_html` used as fallback.

### TipTapEditor.vue — watch fix
Replaced single `JSON.stringify` comparison with type-aware logic:
- `typeof val === 'string'` → compare via `editor.getHTML()`, call `setContent(val, false)`
- object → compare via `JSON.stringify`, call `setContent(val ?? '', false)`

### TipTapEditor.vue — HTML import button
- New toolbar button `HTML↑` with `data-testid="tiptap-import-html-btn"`
- Modal with textarea `data-testid="tiptap-html-input"`
- Apply button `data-testid="tiptap-apply-html-btn"` calls `editor.commands.setContent(htmlInput.trim(), true)`
- TipTap natively converts HTML to ProseMirror JSON on `setContent()`

## Contracts Verified:
- data-testid on all new interactive elements: OK (tiptap-import-html-btn, tiptap-import-html-modal, tiptap-html-input, tiptap-apply-html-btn)
- Only var(--color-*) tokens used in styles: OK
- No hardcoded colors or spacing in .vue files: OK
- npm run lint: OK (exit 0)
- npm run typecheck: OK (exit 0)

## Next:
- testing-agent: e2e tests for HTML import button in TipTap editor

## Blockers:
- none
