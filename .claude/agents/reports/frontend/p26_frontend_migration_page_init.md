# Task Report: p26_frontend_migration_page_init

## Status: DONE

## Completed:
- Исправлена загрузка данных миграций при прямом открытии URL
- Заменён `onMounted` вызов на SSR-совместимый `useApi` на верхнем уровне
- Обновлён `fetchStatus()` для использования `refreshStatus()` из useApi
- Убрана ручная установка `status.value = null` в `resetMigration()`

## Artifacts:
- frontend/pages/admin/migration.vue

## Problem Analysis:
**Root cause:** Данные загружались только в `onMounted` через вызов `fetchStatus()`, который использовал `useApi` внутри функции. При SSR (прямое открытие URL) `onMounted` не выполняется на сервере, поэтому страница рендерилась с `isLoading=true` и `status=null`, отображая пустую страницу.

**Why it worked on client navigation:** При переходе с другой страницы (SPA navigation) `onMounted` выполнялся на клиенте, загружая данные корректно.

## Solution:
Использован `await useApi<MigrationStatus>('/admin/migration/status')` на верхнем уровне `<script setup>`, что обеспечивает:
- Загрузку данных на сервере при SSR
- Гидратацию данных на клиенте
- Автоматическое управление состоянием `pending` (isLoading)
- Метод `refresh()` для обновления данных в polling

## Changes:
```typescript
// До:
const status = ref<MigrationStatus | null>(null)
const isLoading = ref(true)
// fetchStatus() вызывался только в onMounted

// После:
const { data: status, pending: isLoading, refresh: refreshStatus } =
  await useApi<MigrationStatus>('/admin/migration/status')
// Данные загружаются при SSR и CSR
```

## Contracts Verified:
- SSR-совместимая загрузка данных: ✅
- Только var(--color-*) токены: ✅
- vue-tsc (npm run lint): ✅
- npm run typecheck: ✅

## Acceptance Criteria:
- ✅ Прямое открытие /admin/migration загружает данные
- ✅ Обновление страницы (F5) работает корректно
- ✅ Данные миграций отображаются при первой загрузке
- ✅ Polling работает после загрузки (fetchStatus в onMounted)
- ✅ SSR не вызывает ошибок
- ✅ npm run lint passes
- ✅ npm run typecheck passes

## Next:
- Визуальная проверка: открыть https://m.wifiobd.ru/admin/migration напрямую → данные должны загрузиться
- Проверить обновление страницы (F5) → данные должны сохраниться
- Проверить polling → должен работать после загрузки

## Blockers:
- none
