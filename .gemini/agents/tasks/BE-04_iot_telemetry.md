---
id: BE-04
status: TODO
agent: backend-agent
stage: 8 (IoT / OBD2)
priority: MEDIUM
depends_on: []
blocks: [FE-04]
---

# BE-04 — IoT телеметрия (TimescaleDB + Redis Streams + WebSocket)

## Цель

Реализовать полный IoT-пайплайн: приём данных OBD2 → Redis Stream → TimescaleDB hypertable → live WebSocket.

## ⚠️ Перед началом

```bash
read_file backend/app/db/models/user_device.py  # уже есть
list_directory backend/app/api/v1/iot/
# Проверить наличие telemetry.py в models/
```

## Задачи

### 1. Модель `telemetry.py` (`backend/app/db/models/telemetry.py`)

Если отсутствует — создать:

```python
class Telemetry(Base):
    __tablename__ = "telemetry"
    # НЕ id автоинкремент — TimescaleDB требует ts в PK
    device_id: UUID  # FK -> user_device.id
    ts: datetime     # TIMESTAMPTZ, NOT NULL — ось гипертаблицы
    data: dict       # JSONB — сырые OBD2-данные {rpm, speed, temp, ...}

    __table_args__ = (
        PrimaryKeyConstraint('device_id', 'ts'),
    )
```

### 2. Миграция Alembic (TimescaleDB)

```python
def upgrade() -> None:
    # 1. Создать таблицу
    op.create_table('telemetry',
        sa.Column('device_id', postgresql.UUID(), nullable=False),
        sa.Column('ts', sa.DateTime(timezone=True), nullable=False),
        sa.Column('data', postgresql.JSONB(), nullable=False),
        sa.ForeignKeyConstraint(['device_id'], ['user_device.id']),
        sa.PrimaryKeyConstraint('device_id', 'ts'),
    )
    # 2. Переключить в hypertable
    op.execute(
        "SELECT create_hypertable('telemetry', 'ts', "
        "chunk_time_interval => INTERVAL '1 day')"
    )
    # 3. Retention policy из настроек
    op.execute(
        f"SELECT add_retention_policy('telemetry', "
        f"INTERVAL '{settings.TELEMETRY_RETENTION_DAYS} days')"
    )

def downgrade() -> None:
    op.drop_table('telemetry')
    # TimescaleDB автоматически удаляет политику при drop table
```

Именование: `YYYYMMDD_HHMMSS_iot_add_telemetry_hypertable.py`

### 3. IoT API (`backend/app/api/v1/iot/`)

Проверить наличие всех 4 файлов, создать отсутствующие:

**router.py:**
```
POST /api/v1/iot/data
  Auth: Bearer token (require_role("customer"))
  Body: { device_id: UUID, ts: datetime, data: dict }
  → validate device ownership → XADD iot:{device_id} Redis Stream → 202 Accepted

GET /api/v1/iot/devices
  → список устройств текущего пользователя

GET /api/v1/iot/devices/{device_id}/history
  ?from=ISO&to=ISO&bucket=5m
  → time_bucket агрегация из TimescaleDB

WS  /ws/iot/{device_id}
  Auth: ?token=<access_token>
  → live push через Redis Pub/Sub
```

### 4. Celery consumer (Redis Stream → TimescaleDB)

`backend/app/tasks/iot_consumer.py`:
```python
@celery_app.task(name="tasks.consume_iot_stream")
def consume_iot_stream():
    # XREAD COUNT 100 BLOCK 1000 STREAMS iot:* 0
    # Batch INSERT в telemetry через executemany (async session)
    # После успешного insert: XACK + Redis Pub/Sub PUBLISH iot:live:{device_id}
```

Celery Beat: запускать каждые 5 сек.

### 5. WebSocket ConnectionManager

`backend/app/api/v1/iot/connection_manager.py`:
```python
class ConnectionManager:
    # dict[str, list[WebSocket]] — device_id → connections
    async def connect(self, device_id: str, ws: WebSocket) -> None
    async def disconnect(self, device_id: str, ws: WebSocket) -> None
    async def broadcast(self, device_id: str, data: dict) -> None

# Redis Pub/Sub subscriber в lifespan:
# SUBSCRIBE iot:live:{device_id} → broadcast к подключённым WS
```

**Важно:** `try/finally` в WebSocket endpoint гарантирует disconnect.

### 6. Dashboard-запрос (time_bucket)

В repository НЕ делать raw SELECT *. Только агрегация:
```sql
SELECT time_bucket('5 minutes', ts) AS bucket,
       avg((data->>'rpm')::float)   AS avg_rpm,
       avg((data->>'speed')::float) AS avg_speed,
       max((data->>'temp')::float)  AS max_temp
FROM telemetry
WHERE device_id = :device_id
  AND ts BETWEEN :from AND :to
GROUP BY bucket
ORDER BY bucket ASC
```

## Контракты

- `settings.TELEMETRY_RETENTION_DAYS` — обязательно в config.py, default=90
- WebSocket auth: только через `?token=` query param
- НИКОГДА не утекать WebSocket-соединения (try/finally)
- Device ownership: проверять что `device_id` принадлежит `current_user`

## Критерии готовности

- [ ] `alembic check` чисто
- [ ] `create_hypertable` вызывается в migration upgrade()
- [ ] POST /iot/data → XADD в Redis, 202 без ожидания записи в БД
- [ ] Celery consumer: batch insert каждые 5 сек
- [ ] WS /ws/iot/{device_id} — получает live данные < 1 сек после POST /iot/data
- [ ] GET /iot/devices/{id}/history — возвращает time_bucket агрегацию

## Отчёт

`.gemini/agents/reports/backend/BE-04.md`
