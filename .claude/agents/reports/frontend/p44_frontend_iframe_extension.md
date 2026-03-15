## Status: DONE

## Completed:
- Created `frontend/extensions/IframeExtension.ts` — TipTap Node extension with parseHTML, renderHTML, addNodeView, addCommands
- Added `IframeExtension` import and registration in `TipTapEditor.vue` (after Youtube extension)
- Added `IframeExtension` import and registration in `TipTapViewer.vue` (after Youtube extension)
- Added `IframeExtension` import and registration in `URichEditor.vue` (after Typography extension)
- Added toolbar button with icon `ph:frame-corners-bold`, `data-testid="editor-iframe-insert"`, `aria-label="Вставить iframe"` in `TipTapEditor.vue`
- Added iframe insert modal dialog in `TipTapEditor.vue` with two fields: URL (src) and height, using the same `md-modal` pattern as existing HTML/Markdown dialogs
- Added `.iframe-wrapper` CSS (using only `var(--color-*)` tokens) to all three components in `<style scoped>` blocks
- Added `.post-content .iframe-wrapper` and `.tiptap-viewer .iframe-wrapper` CSS to `frontend/assets/css/main.css`

## Artifacts:
- `frontend/extensions/IframeExtension.ts` (new file)
- `frontend/components/blog/TipTapEditor.vue` (modified)
- `frontend/components/blog/TipTapViewer.vue` (modified)
- `frontend/components/U/URichEditor.vue` (modified)
- `frontend/assets/css/main.css` (modified)

## Contracts Verified:
- data-testid on interactive elements: OK (`editor-iframe-insert`, `tiptap-iframe-modal`, `tiptap-iframe-src-input`, `tiptap-iframe-height-input`, `tiptap-apply-iframe-btn`)
- Only var(--color-*) tokens in styles: OK (no hex values)
- Mobile-first breakpoints: OK (no changes to layout)
- npm run lint: OK (exit 0, no errors)
- npm run typecheck (vue-tsc --noEmit): OK (exit 0, no errors)

## Accessibility:
- Toolbar button has `aria-label="Вставить iframe"` and `title="Вставить iframe"`
- Modal dialog has `role="dialog"`, `aria-modal="true"`, `aria-label="Вставить iframe"`
- Close button has `aria-label="Закрыть"`
- Apply button disabled when src is empty (prevents invalid submit)

## Next:
- testing-agent: e2e tests for iframe insert in TipTapEditor — check `data-testid="editor-iframe-insert"` click, modal open, src input, apply button
- backend-agent: ensure p44_backend_iframe_sanitize allows iframe tags via Bleach

## Blockers:
- none
