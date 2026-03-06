.PHONY: test test-e2e check

test:
	pytest tests/unit tests/integration

test-e2e:
	pytest tests/e2e/ --headed

check:
	cd backend && ruff check app/ --fix && ruff check app/ && mypy app/ --ignore-missing-imports
	cd frontend && npm run lint
	cd backend && alembic check && alembic heads
	pytest tests/ -x -v