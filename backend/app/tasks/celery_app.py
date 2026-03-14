# Module: tasks/celery_app.py | Agent: backend-agent | Task: phase6_notifications
from celery import Celery
from celery.signals import worker_process_init
from app.core.config import settings
from app.db.redis import reset_redis_client
from app.db.opencart_session import reset_oc_engine
from app.db.celery_session import reset_celery_engine

@worker_process_init.connect
def reset_connections_on_fork(**kwargs):
    """Ensure each worker process creates its own connections with a new event loop."""
    reset_redis_client()
    reset_oc_engine()
    reset_celery_engine()

# CELERY_BROKER_URL, CELERY_RESULT_BACKEND will be picked up from settings automatically 
# if we use config_from_object with the 'CELERY' namespace.
celery_app = Celery("wifiobd")
celery_app.conf.update(
    broker_url=settings.CELERY_BROKER_URL,
    result_backend=settings.CELERY_RESULT_BACKEND,
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    # Force Celery to import tasks on startup
    include=[
        "app.tasks.notifications.dispatcher",
        "app.tasks.currency",
        "app.tasks.inventory",
        "app.tasks.search",
        "app.tasks.migration_tasks",
    ]
)

celery_app.conf.beat_schedule = {
    "release-stale-reservations-every-15-mins": {
        "task": "tasks.release_stale_reservations",
        "schedule": 900.0, # 15 minutes
    },
}

# Optional: Configuration from environment variables
# celery_app.config_from_object('app.core.config', namespace='CELERY')

if __name__ == "__main__":
    celery_app.start()
