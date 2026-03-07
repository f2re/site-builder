#!/usr/bin/env python3
"""
LocalContextMiddleware
Сканирует окружение при старте и выводит сводку для агента.
"""
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent


def check_running(port: int) -> bool:
    try:
        subprocess.check_call(
            f"nc -z localhost {port}",
            shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        return True
    except subprocess.CalledProcessError:
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
    print("🚀 Services:")
    for port, name in services.items():
        status = "✅ RUNNING" if check_running(port) else "❌ STOPPED"
        print(f"  {name:18} | {status}")

    # 2. Config check
    print("\n📁 Config Files:")
    configs = [".env", "backend/.env", "frontend/.env", "docker-compose.yml"]
    for cfg in configs:
        exists = "✅" if (ROOT / cfg).exists() else "❌"
        print(f"  {exists} {cfg}")

    # 3. DB Migrations
    try:
        res = subprocess.run(
            "cd backend && alembic heads",
            shell=True, capture_output=True, text=True
        )
        heads = res.stdout.strip().split("\n")
        status = "✅ OK" if len(heads) == 1 else f"❌ ERROR ({len(heads)} heads)"
        print(f"\n📦 Alembic Migration Status: {status}")
    except Exception:
        print("\n📦 Alembic Migration Status: ❌ UNKNOWN")

    print("\n--- Context Scan Complete ---")


if __name__ == "__main__":
    scan()
