#!/usr/bin/env python3
"""
LocalContextMiddleware
Сканирует окружение при старте и выводит сводку для агента.
"""
import subprocess
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent

CMD_TIMEOUT = 10  # секунд на каждую быструю проверку


def check_running(port: int) -> bool:
    try:
        subprocess.check_call(
            f"nc -z localhost {port}",
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=CMD_TIMEOUT
        )
        return True
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return False


def scan() -> None:
    print("\n=== Local Context Scan ===")

    # 1. Services status
    services = {
        8000: "Backend (FastAPI)",
        3000: "Frontend (Nuxt)",
        5432: "PostgreSQL",
        6379: "Redis",
        7700: "Meilisearch",
        9000: "MinIO"
    }
    print("\U0001f680 Services:")
    for port, name in services.items():
        status = "\u2705 RUNNING" if check_running(port) else "\u274c STOPPED"
        print(f"  {name:18} | {status}")

    # 2. Config check
    print("\n\U0001f4c1 Config Files:")
    configs = [".env", "backend/.env", "frontend/.env", "docker-compose.yml"]
    for cfg in configs:
        exists = "\u2705" if (ROOT / cfg).exists() else "\u274c"
        print(f"  {exists} {cfg}")

    # 3. DB Migrations
    try:
        res = subprocess.run(
            "cd backend && alembic heads",
            shell=True, capture_output=True, text=True,
            timeout=30
        )
        heads = [h for h in res.stdout.strip().split("\n") if h.strip()]
        status = "\u2705 OK" if len(heads) == 1 else f"\u274c ERROR ({len(heads)} heads)"
        print(f"\n\U0001f4e6 Alembic Migration Status: {status}")
    except subprocess.TimeoutExpired:
        print("\n\U0001f4e6 Alembic Migration Status: \u23f1 TIMEOUT (>30s)")
    except Exception:
        print("\n\U0001f4e6 Alembic Migration Status: \u274c UNKNOWN")

    print("\n--- Context Scan Complete ---")


if __name__ == "__main__":
    scan()
