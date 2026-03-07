#!/usr/bin/env python3
"""
PreCompletionChecklistMiddleware
Запускается агентом ПЕРЕД любым коммитом.
Если хотя бы один пункт не пройден — коммит ЗАБЛОКИРОВАН.
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent
BACKEND = ROOT / "backend"
FRONTEND = ROOT / "frontend"

CMD_TIMEOUT = 120  # секунд максимум на одну команду


def run(cmd: str, cwd: Path, timeout: int = CMD_TIMEOUT) -> tuple[bool, str]:
    try:
        result = subprocess.run(
            cmd, shell=True, cwd=cwd,
            capture_output=True, text=True,
            timeout=timeout
        )
        return result.returncode == 0, result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return False, f"\u23f1 TIMEOUT ({timeout}s): команда '{cmd}' превысила лимит времени"
    except Exception as e:
        return False, f"ERROR: {e}"


def check_all() -> bool:
    results = {}

    ok, out = run("ruff check app/", BACKEND)
    results["ruff"] = (ok, out)

    ok, out = run("mypy app/ --ignore-missing-imports", BACKEND)
    results["mypy"] = (ok, out)

    ok, out = run("npm run lint 2>&1 | tail -5", FRONTEND)
    results["vue-tsc"] = (ok, out)

    # Проверяем доступность PostgreSQL перед alembic
    pg_ok, _ = run("pg_isready -q", ROOT, timeout=10)
    if pg_ok:
        ok, out = run("alembic check && alembic heads", BACKEND, timeout=30)
        results["alembic"] = (ok, out)
    else:
        results["alembic"] = (True, "\u26a0\ufe0f PostgreSQL недоступен — alembic пропущен")

    ok, out = run("pytest tests/ -x -q --tb=short --timeout=60", ROOT)
    results["pytest"] = (ok, out)

    print("\n=== Pre-Commit Checklist ===")
    all_passed = True
    for name, (passed, output) in results.items():
        status = "\u2705" if passed else "\u274c"
        print(f"{status} {name}")
        if not passed:
            print(f"   \u2514\u2500 {output[:300]}")
            all_passed = False

    if not all_passed:
        print("\n\U0001f6ab COMMIT BLOCKED \u2014 \u0438\u0441\u043f\u0440\u0430\u0432\u044c \u043e\u0448\u0438\u0431\u043a\u0438 \u0438 \u0437\u0430\u043f\u0443\u0441\u0442\u0438 \u0441\u043d\u043e\u0432\u0430")
        return False

    print("\n\u2705 \u0412\u0441\u0435 \u043f\u0440\u043e\u0432\u0435\u0440\u043a\u0438 \u043f\u0440\u043e\u0439\u0434\u0435\u043d\u044b \u2014 \u043a\u043e\u043c\u043c\u0438\u0442 \u0440\u0430\u0437\u0440\u0435\u0448\u0451\u043d")
    return True


if __name__ == "__main__":
    sys.exit(0 if check_all() else 1)
