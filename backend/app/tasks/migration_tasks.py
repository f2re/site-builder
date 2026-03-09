# Module: tasks/migration_tasks.py | Agent: backend-agent | Task: p17_backend_celery_migration_fix
import asyncio
from uuid import UUID
from app.tasks.celery_app import celery_app
from app.db.celery_session import CelerySessionLocal
from app.api.v1.admin.migration_service import MigrationService
from app.api.v1.admin.migration_repository import MigrationRepository
from app.core.logging import logger


@celery_app.task(name="tasks.run_migration_task", bind=True, max_retries=3)
def run_migration_task(self, job_id: str):
    """
    Celery task to run a specific migration job.
    Uses Redis lock to prevent concurrent execution of the same job.
    """
    async def _run():
        from app.db.celery_session import celery_engine  # noqa: PLC0415
        from app.db.opencart_session import oc_engine  # noqa: PLC0415
        from app.db.models.migration import MigrationStatus  # noqa: PLC0415
        from app.db.redis import get_redis  # noqa: PLC0415

        lock_key = f"migration_lock:{job_id}"
        lock_ttl = 300  # 5 minutes — enough for one batch

        redis = await get_redis()
        # SET NX EX — atomic acquire
        acquired = await redis.set(lock_key, "1", nx=True, ex=lock_ttl)
        if not acquired:
            logger.warning("migration_task_skipped_locked", job_id=job_id)
            return

        session = None
        try:
            session = CelerySessionLocal()
            repo = MigrationRepository(session)
            service = MigrationService(repo, session)
            await service.run_batch(UUID(job_id))
        except Exception as exc:
            logger.error("migration_task_failed", job_id=job_id, error=str(exc))
            if session:
                try:
                    await repo.update_job_status(UUID(job_id), MigrationStatus.FAILED)
                except Exception as mark_exc:
                    logger.error("migration_mark_failed_error", job_id=job_id, error=str(mark_exc))
            raise
        finally:
            await redis.delete(lock_key)
            if session:
                await session.close()
            await celery_engine.dispose()
            await oc_engine.dispose()

    try:
        return asyncio.run(_run())
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)
