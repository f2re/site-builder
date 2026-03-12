.PHONY: test test-e2e check seed-e2e seed-e2e-reset dev-start test-e2e-ci feature-test install-hooks

install-hooks:
	bash scripts/install-hooks.sh

test:
	pytest tests/unit tests/integration

check:
	cd backend && ruff check app/ --fix && ruff check app/ && mypy app/ --ignore-missing-imports
	cd frontend && npm run lint
	cd backend && alembic check && alembic heads
	pytest tests/ -x -v

seed-e2e:
	cd backend && python -m scripts.seed_e2e

seed-e2e-reset:
	cd backend && python -m scripts.seed_e2e --reset

dev-start:
	python scripts/dev_start.py &
	@echo "⏳ Ожидание сервисов..."
	@sleep 5
	@curl -sf http://localhost:8000/health && echo "✅ Backend OK"
	@curl -sf http://localhost:3000 && echo "✅ Frontend OK"

test-e2e:
	pytest tests/e2e/ -v --headed -s

test-e2e-ci:
	CI=true pytest tests/e2e/ -v --screenshot=on

feature-test: seed-e2e test-e2e
	@echo "✅ Фича протестирована"
