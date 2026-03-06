# e2e_protocol.md — E2E Автоматизация: Протокол агентов

> Часть документации оркестратора. Точка входа: [CLAUDE.md](../../CLAUDE.md)

---

## Задачи фазы E2E (Phase 8, подфаза e2e)

| task_id | Агент | Зависит от | Описание |
|---|---|---|---|
| `p8_e2e_backend_001` | backend-agent | p2, p3, p4 | Создать `backend/scripts/seed_e2e.py` |
| `p8_e2e_frontend_001` | frontend-agent | p7 | Расставить все `data-testid` по контракту |
| `p8_e2e_testing_001` | testing-agent | p8_e2e_backend_001 + p8_e2e_frontend_001 | Запустить E2E, зафиксировать результат |

---

## Порядок запуска

```
backend-agent  p8_e2e_backend_001   (параллельно с frontend)
frontend-agent p8_e2e_frontend_001  (параллельно с backend)
          ↓ оба завершены
testing-agent  p8_e2e_testing_001   (запускает тесты, пишет отчёт)
```

---

## Slash-команды для запуска E2E-цикла

```bash
/agents:run backend-agent p8_e2e_backend_001
/agents:run frontend-agent p8_e2e_frontend_001

# После завершения обоих:
/agents:run testing-agent p8_e2e_testing_001

/agents:status
```

---

## Что делает testing-agent (p8_e2e_testing_001)

1. Проверяет доступность всех сервисов (порты 3000, 8000, 7700)
2. Запускает `python -m scripts.seed_e2e` для засева данных
3. Устанавливает зависимости: `pip install pytest playwright requests` + `playwright install chromium`
4. Прогоняет `pytest tests/e2e/ -v --headed -s` с логом в `.logs/e2e.log`
5. Анализирует каждое падение: тест-код / отсутствующий testid / API / seed-данные
6. Исправляет проблемы в тест-коде (conftest, fixture)
7. Эскалирует блокеры по frontend/backend через отчёт

---

## Контракт data-testid

Полный реестр всех обязательных `data-testid`:
`.claude/agents/contracts/e2e_testid_contract.md`

---

## Итоговый отчёт

testing-agent пишет отчёт в:
`.claude/agents/reports/testing/p8_e2e_testing_001.md`

Формат — таблица PASS/FAIL по каждому `test_0*.py` + список блокеров с указанием ответственного агента.

---

## Повтор цикла после фиксов

Если testing-agent нашёл блокеры:
1. frontend-agent исправляет data-testid → обновляет отчёт
2. backend-agent дополняет seed / фиксит API → обновляет отчёт
3. testing-agent повторяет прогон: `/agents:run testing-agent p8_e2e_testing_001`

Цикл повторяется до статуса `## Status: DONE` во всех отчётах.
