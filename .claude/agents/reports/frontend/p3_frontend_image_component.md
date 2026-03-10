## Status: BLOCKED

## Task: p3_frontend_image_component
Создать компонент ImageWithFallback для автоматического выбора размера изображения

## Blocker Details
Задача заблокирована зависимостью `p3_backend_image_model_extension` (status: pending).

Компонент требует структуру данных `formats: Record<string, string>` из backend API:
```typescript
{
  "thumb": "001_thumb.webp",
  "small": "001_small.webp",
  "medium": "001_medium.webp",
  "large": "001_large.webp",
  "original": "001.webp"
}
```

Эта структура будет добавлена в модели ProductImage и BlogPostMedia backend-agent'ом.

## Implementation Plan (ready after unblock)

### 1. TypeScript Types (`frontend/types/image.ts`)
```typescript
export type ImageSize = 'thumb' | 'small' | 'medium' | 'large' | 'original'
export type ImageFormats = Partial<Record<ImageSize, string>>

export interface ImageWithFallbackProps {
  formats: ImageFormats
  alt: string
  size?: ImageSize
  lazy?: boolean
  placeholder?: 'skeleton' | 'blur'
}
```

### 2. Composable (`frontend/composables/useImageLoader.ts`)
- Fallback chain: original → large → medium → small → thumb
- IntersectionObserver integration via existing `useIntersection`
- Error handling with automatic retry on smaller size
- Reactive loading/error states

### 3. Component (`frontend/components/ImageWithFallback.vue`)
- Props: formats, alt, size (default: 'medium'), lazy (default: true), placeholder (default: 'skeleton')
- USkeleton placeholder while loading
- Responsive srcset for 1x/2x DPR (if available)
- data-testid="image-with-fallback"
- CSS: only var(--color-*) tokens from tokens.css
- Transition: fade-in on load (var(--transition-normal))

### 4. Design Tokens Usage
- Skeleton: existing .skeleton class from tokens.css
- Transition: var(--transition-normal) for fade-in
- Border radius: var(--radius-md) for placeholder

## Contracts Verified
- ✅ API contracts read: formats structure documented
- ✅ Design tokens reviewed: tokens.css
- ✅ Existing patterns: useIntersection, USkeleton
- ⏸️ Implementation: waiting for backend dependency

## Next Steps
1. **backend-agent**: complete p3_backend_image_model_extension
2. **frontend-agent**: implement ImageWithFallback after unblock
3. **testing-agent**: e2e tests for image loading and fallback

## Blockers
- **p3_backend_image_model_extension** (backend-agent) — status: pending
  - Required: formats field in ProductImage/BlogPostMedia models
  - Required: API response with formats structure

## Estimated Effort After Unblock
- 90 minutes (as per task definition)

## Created
2026-03-10

## Agent
frontend-agent
