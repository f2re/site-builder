# API Contracts между агентами

## API Path & BaseURL Policy

1. **apiBase** в `runtimeConfig` **ОБЯЗАН** включать версию (например, `/api/v1`).
2. **ЗАПРЕЩЕНО** вручную добавлять `/api/v1` или `/v1` в относительные пути.
3. Все пути в композаблах должны начинаться с `/` относительно `apiBase`.

```typescript
// composables/useProducts.ts
const { apiBase } = useRuntimeConfig()

// ✅ ПРАВИЛЬНО:
const { data: products } = await useFetch('/products', { baseURL: apiBase })

// ❌ НЕПРАВИЛЬНО:
const { data: products } = await useFetch('/api/v1/products')
```

---

## Auth & Profile Flow Contract

### Token Naming
- В фронтенд-композаблах использовать строго `accessToken` (не `token`, не `jwt`).
- Refresh token хранится в `httpOnly` cookie.

### Full User Object
Любой эндпоинт авторизации (`login`, `callback`, `telegram`) **ОБЯЗАН** возвращать полную модель `UserResponse`:

```python
# backend/app/api/v1/auth/schemas.py
class AuthResponse(BaseModel):
    accessToken: str
    refreshToken: str  # через cookie
    user: UserResponse
```

### Re-hashing Email
При обновлении `email` в `UserRepository` бэкенд-агент **ОБЯЗАН** пересчитывать `email_hash` (blind index).

---

## UI Parity Rule

Любая навигационная ссылка, добавленная в мобильное меню (Drawer), **ДОЛЖНА** иметь аналог в десктопной версии (Header/Sidebar), если иное не оговорено.

---

## Pydantic Schemas Contract

### Request/Response модели
Каждый эндпоинт **MUST** иметь отдельные Request + Response схемы:

```python
# backend/app/api/v1/products/schemas.py

class ProductCreate(BaseModel):
    """Request schema для создания товара"""
    name: str
    slug: str
    price: Decimal
    category_id: UUID

class ProductResponse(BaseModel):
    """Response schema товара"""
    id: UUID
    name: str
    slug: str
    price: Decimal
    category: CategoryResponse
    stock: int
    
    model_config = ConfigDict(from_attributes=True)
```

### DI via Depends
Все сервисы **MUST** принимать зависимости через `Depends`:

```python
# backend/app/api/v1/products/router.py

@router.get("/", response_model=list[ProductResponse])
async def list_products(
    service: ProductService = Depends(),
    pagination: PaginationParams = Depends(),
):
    return await service.list_all(pagination)
```

---

## IoT WebSocket Contract

### Authentication
WebSocket подключение **MUST** включать токен в query parameter:

```
ws://host/api/v1/iot/ws/{device_id}?token=<access_token>
```

### Data Pipeline
```
OBD device → POST /api/v1/iot/data → Redis Stream → Celery → TimescaleDB
                                           ↓
                                    WebSocket broadcast
```

### Dashboard Queries
**ALWAYS use `time_bucket`** (TimescaleDB), never raw `SELECT *`:

```sql
SELECT time_bucket('5 minutes', ts) AS bucket,
       avg((data->>'rpm')::float)    AS avg_rpm
FROM   telemetry
WHERE  device_id = :device_id
  AND  ts > NOW() - INTERVAL '1 hour'
GROUP  BY bucket
ORDER  BY bucket
```

---

## Design Token Contract

### CSS Custom Properties
Все цвета/отступы **MUST** использовать переменные из `tokens.css`:

```css
/* ✅ ПРАВИЛЬНО */
.button {
  background: var(--color-accent);
  color: var(--color-on-accent);
  padding: var(--spacing-md);
}

/* ❌ НЕПРАВИЛЬНО */
.button {
  background: #e63946;
  color: #ffffff;
  padding: 16px;
}
```

### Theme Switching
- `themeStore.toggle()` **MUST** обновлять `document.documentElement.dataset.theme`
- Тема **MUST** сохраняться в `localStorage` key `theme`
- SSR: читать тему из cookie `theme` (httpOnly=false)

---

## Error Handling Contract

### Backend HTTP Errors
Все ошибки **MUST** возвращать стандартизированный формат:

```python
# backend/app/core/exceptions.py

class APIException(Exception):
    def __init__(self, status_code: int, detail: str, code: str):
        self.status_code = status_code
        self.detail = detail
        self.code = code  # машинный код ошибки
```

Пример ответа:
```json
{
  "error": {
    "code": "PRODUCT_NOT_FOUND",
    "message": "Товар с ID abc-123 не найден",
    "status_code": 404
  }
}
```

### Frontend Error Boundaries
Все async действия **MUST** обрабатывать ошибки через `useFetch` / `useAsyncData`:

```typescript
const { data, error, pending } = await useFetch('/products')

if (error.value) {
  // Показать toast с ошибкой
  toast.error(error.value.data.detail)
}
```

---

## Rate Limiting Contract

### Backend
- `/api/v1/auth/*` — 10 запросов/минуту
- `/api/v1/checkout` — 5 запросов/минуту
- `/api/v1/payments/*` — 10 запросов/минуту

Использовать `slowapi` для FastAPI.

### Nginx
```nginx
limit_req_zone $binary_remote_addr zone=auth:10m rate=10r/m;
limit_req_zone $binary_remote_addr zone=checkout:10m rate=5r/m;
```

---

## Caching Contract

### Redis Keys Naming
```
auth:session:{session_id}
auth:token:blacklist:{jti}
cdek:pvz:{city_code}
cbr:rates:{YYYY-MM-DD}
cart:{user_id|session_id}
stock:{product_id}
iot:stream:{device_id}
```

### TTL Values
| Key | TTL |
|-----|-----|
| `auth:session` | 7 дней |
| `cdek:pvz` | 6 часов |
| `cbr:rates` | 26 часов |
| `cart` | 30 минут (с продлением) |
| `stock` | 5 минут |
