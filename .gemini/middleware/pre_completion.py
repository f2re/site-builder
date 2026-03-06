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


def run(cmd: str, cwd: Path) -> tuple[bool, str]:
    result = subprocess.run(
        cmd, shell=True, cwd=cwd,
        capture_output=True, text=True
    )
    return result.returncode == 0, result.stdout + result.stderr


def check_all() -> bool:
    results = {}

    ok, out = run("ruff check app/", BACKEND)
    results["ruff"] = (ok, out)

    ok, out = run("mypy app/ --ignore-missing-imports", BACKEND)
    results["mypy"] = (ok, out)

    ok, out = run("npm run lint 2>&1 | tail -5", FRONTEND)
    results["vue-tsc"] = (ok, out)

    ok, out = run("alembic check && alembic heads", BACKEND)
    results["alembic"] = (ok, out)

    ok, out = run("pytest tests/ -x -q --tb=short", ROOT)
    results["pytest"] = (ok, out)

    print("\n=== Pre-Commit Checklist ===")
    all_passed = True
    for name, (passed, output) in results.items():
        status = "✅" if passed else "❌"
        print(f"{status} {name}")
        if not passed:
            print(f"   └─ {output[:300]}")
            all_passed = False

    if not all_passed:
        print("\n🚫 COMMIT BLOCKED — исправь ошибки и запусти снова")
        return False

    print("\n✅ Все проверки пройдены — коммит разрешён")
    return True


if __name__ == "__main__":
    sys.exit(0 if check_all() else 1)