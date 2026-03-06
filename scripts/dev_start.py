#!/usr/bin/env python3
import subprocess
import sys
import time

def start_services():
    print("Starting PostgreSQL and Redis...")
    subprocess.run(["brew", "services", "start", "postgresql@16"], check=False)
    subprocess.run(["brew", "services", "start", "redis"], check=False)
    print("Starting Meilisearch...")
    subprocess.Popen(["./meilisearch", "--master-key=$MEILI_MASTER_KEY"], shell=True)
    print("Starting Backend...")
    subprocess.Popen(["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"], cwd="backend")
    print("Starting Celery...")
    subprocess.Popen(["celery", "-A", "app.tasks.celery_app", "worker", "-B", "--loglevel=warning"], cwd="backend")
    print("Starting Frontend...")
    subprocess.Popen(["npm", "run", "dev"], cwd="frontend")
    print("All services started.")

def stop_services():
    print("Stopping services...")
    subprocess.run(["pkill", "-f", "uvicorn"])
    subprocess.run(["pkill", "-f", "celery"])
    subprocess.run(["pkill", "-f", "npm"])
    subprocess.run(["pkill", "-f", "meilisearch"])
    subprocess.run(["brew", "services", "stop", "postgresql@16"], check=False)
    subprocess.run(["brew", "services", "stop", "redis"], check=False)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "stop":
        stop_services()
    else:
        start_services()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            stop_services()