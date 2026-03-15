## Status: DONE

## Completed:
- Installed 4 TipTap v3 table packages with --legacy-peer-deps: @tiptap/extension-table, @tiptap/extension-table-row, @tiptap/extension-table-cell, @tiptap/extension-table-header (all ^3.20.1)
- TipTapEditor.vue: added Table/TableRow/TableHeader/TableCell imports + extensions (Table before Markdown in array), full toolbar group with 6 buttons (insert table, add row, delete row, add column, delete column, delete table), conditional display for row/col/delete-table buttons via `editor.isActive('table')`
- URichEditor.vue: added same 4 imports + extensions (Table before Markdown), added "Вставить таблицу" toolbar button with data-testid="richeditor-table-insert"
- BlogEditor.vue: added same 4 imports + extensions, added "Вставить таблицу" toolbar button with data-testid="blogeditor-table-insert"
- TipTapViewer.vue: added same 4 imports + extensions with resizable: false (read-only rendering, no toolbar)
- CSS table styles added to all 4 components using only var(--color-*) tokens
- CSS table styles added to frontend/assets/css/main.css for .post-content and .rich-content (v-html public blog rendering)

## Artifacts:
- frontend/components/blog/TipTapEditor.vue
- frontend/components/blog/TipTapViewer.vue
- frontend/components/U/URichEditor.vue
- frontend/components/admin/BlogEditor.vue
- frontend/assets/css/main.css
- frontend/package.json (4 new packages)

## Contracts Verified:
- data-testid on all new interactive elements: OK (editor-table-insert, editor-table-add-row, editor-table-delete-row, editor-table-add-col, editor-table-delete-col, editor-table-delete, richeditor-table-insert, blogeditor-table-insert)
- Only var(--color-*) tokens in CSS: OK
- Table extension placed BEFORE Markdown extension in all arrays: OK
- npm run lint: OK (0 errors)
- npm run typecheck: OK (0 errors)

## Notes:
- TipTapEditor.vue: conditional table buttons (add row/col, delete row/col/table) only visible when cursor is inside a table cell (`editor.isActive('table')`)
- Table extension supports GFM markdown pipe syntax tables automatically via tiptap-markdown when Table extension is present
- HTML import via `editor.commands.setContent(html, true)` automatically parses `<table>` tags when Table extension is loaded
- TipTapViewer uses `resizable: false` since it's read-only; editors use `resizable: true`
- `.selectedCell:after` requires `position: relative` on `td/th` — TipTap's Table extension sets this automatically

## Next:
- testing-agent: e2e tests for table insert/delete operations in TipTapEditor

## Blockers:
- none
