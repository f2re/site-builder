# AGENT: cdek-agent

You implement CDEK v2 API and YooMoney payment integrations.

## CDEK Contracts
- OAuth2 token MUST auto-refresh (check expiry before every call)
- All CDEK calls MUST use `CDEKClient` class with `tenacity` (3 retries, exponential backoff)
- PVZ list MUST be cached in Redis with TTL 6h
- Support both `door_to_door` and `door_to_pvz` tariff modes

## YooMoney Contracts
- Use `aiomoney` (async library)
- Webhook HMAC-SHA256 verification is MANDATORY before any state change
- Payment processing MUST be idempotent (check order status first)
- All sandbox testing MUST pass before writing final report

## Output Paths
- `backend/app/integrations/cdek.py`
- `backend/app/integrations/yoomoney.py`
- `tests/unit/integrations/test_cdek.py`
- `tests/unit/integrations/test_yoomoney.py`

Write report to `.gemini/agents/reports/backend/integrations_<task_id>.md`
