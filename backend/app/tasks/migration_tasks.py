# Module: tasks/migration_tasks.py | Agent: backend-agent | Task: p17_backend_celery_migration_fix
import asyncio
from uuid import UUID
from app.tasks.celery_app import celery_app
from app.db.session import AsyncSessionLocal
from app.api.v1.admin.migration_service import MigrationService
from app.api.v1.admin.migration_repository import MigrationRepository
from app.core.logging import logger


@celery_app.task(name="tasks.run_migration_task", bind=True, max_retries=3)
def run_migration_task(self, job_id: str):
    """
    Celery task to run a specific migration job.
    """
    async def _run():
        from app.db.session import engine as pg_engine  # noqa: PLC0415
        from app.db.opencart_session import oc_engine  # noqa: PLC0415
        from app.db.models.migration import MigrationStatus  # noqa: PLC0415

        session = None
        try:
            session = AsyncSessionLocal()
            repo = MigrationRepository(session)
            service = MigrationService(repo, session)
            await service.run_batch(UUID(job_id))
        except Exception as exc:
            logger.error("migration_task_failed", job_id=job_id, error=str(exc))
            # Mark job as FAILED in the same event loop
            if session:
                try:
                    await repo.update_job_status(UUID(job_id), MigrationStatus.FAILED)
                except Exception as mark_exc:
                    logger.error("migration_mark_failed_error", job_id=job_id, error=str(mark_exc))
            raise
        finally:
            # Close session first
            if session:
                await session.close()
            # Dispose engines INSIDE the running event loop to prevent
            # "RuntimeError: Event loop is closed" from asyncpg/aiomysql
            # pool cleanup after asyncio.run() closes the loop.
            await pg_engine.dispose()
            await oc_engine.dispose()

    try:
        return asyncio.run(_run())
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)

