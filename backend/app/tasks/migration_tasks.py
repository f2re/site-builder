# Module: tasks/migration_tasks.py | Agent: backend-agent | Task: opencart_migration
import asyncio
from uuid import UUID
from app.tasks.celery_app import celery_app
from app.db.session import AsyncSessionLocal
from app.api.v1.admin.migration_service import MigrationService
from app.api.v1.admin.migration_repository import MigrationRepository
from app.core.logging import logger

@celery_app.task(name="tasks.run_migration_task", bind=True, max_retries=1)
def run_migration_task(self, job_id: str):
    """
    Celery task to run a specific migration job.
    """
    async def _run():
        from app.db.session import engine as pg_engine
        from app.db.opencart_session import oc_engine
        try:
            async with AsyncSessionLocal() as session:
                repo = MigrationRepository(session)
                service = MigrationService(repo, session)
                await service.run_batch(UUID(job_id))
        finally:
            # Dispose engines INSIDE the running event loop to prevent
            # "RuntimeError: Event loop is closed" from asyncpg/aiomysql
            # pool cleanup after asyncio.run() closes the loop.
            await pg_engine.dispose()
            await oc_engine.dispose()

    try:
        return asyncio.run(_run())
    except Exception as exc:
        logger.error("migration_task_failed", job_id=job_id, error=str(exc))
        raise self.retry(exc=exc, countdown=60)
