# Module: tasks/migration_tasks.py | Agent: backend-agent | Task: p17_backend_celery_migration_fix
from uuid import UUID
from app.tasks.celery_app import celery_app
from app.api.v1.admin.migration_service import MigrationService
from app.api.v1.admin.migration_repository import MigrationRepository
from app.core.logging import logger

import asyncio


@celery_app.task(name="tasks.run_migration_task", bind=True, max_retries=3)
def run_migration_task(self, job_id: str):
    """
    Celery task to run a specific migration job.
    Each invocation creates a fresh event loop via asyncio.run().
    All async engines/sessions are created and disposed within that single loop lifetime.
    """
    async def _run() -> bool:
        """Returns True if the job should be re-triggered."""
        from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession  # noqa: PLC0415
        from sqlalchemy.pool import NullPool  # noqa: PLC0415
        from app.db.models.migration import MigrationStatus  # noqa: PLC0415
        from app.db.redis import get_redis_client  # noqa: PLC0415
        from app.db.opencart_session import _build_oc_url  # noqa: PLC0415
        from app.core.config import settings  # noqa: PLC0415

        lock_key = f"migration_lock:{job_id}"
        lock_ttl = 300  # 5 minutes max per batch

        redis = get_redis_client()
        acquired = await redis.set(lock_key, "1", nx=True, ex=lock_ttl)
        if not acquired:
            logger.warning("migration_task_skipped_locked", job_id=job_id)
            return False

        # Create engines LOCAL to this event loop — no global state issues
        pg_engine = create_async_engine(settings.DATABASE_URL, poolclass=NullPool)
        oc_engine = create_async_engine(_build_oc_url(), poolclass=NullPool, pool_pre_ping=True)

        SessionLocal = async_sessionmaker(
            bind=pg_engine, class_=AsyncSession,
            expire_on_commit=False, autocommit=False, autoflush=False,
        )
        OCSessionLocal = async_sessionmaker(bind=oc_engine, expire_on_commit=False)

        # Monkey-patch OCAsyncSessionLocal for MigrationService
        import app.db.opencart_session as oc_mod  # noqa: PLC0415
        original_oc_factory = oc_mod.OCAsyncSessionLocal
        oc_mod.OCAsyncSessionLocal = lambda: OCSessionLocal()

        session = None
        should_retrigger = False
        try:
            session = SessionLocal()
            repo = MigrationRepository(session)
            service = MigrationService(repo, session)
            should_retrigger = await service.run_batch(UUID(job_id))
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
            await pg_engine.dispose()
            await oc_engine.dispose()
            # Restore original factory
            oc_mod.OCAsyncSessionLocal = original_oc_factory

        return should_retrigger

    try:
        should_retrigger = asyncio.run(_run())
        if should_retrigger:
            run_migration_task.delay(job_id)
            logger.info("migration_task_dispatched", job_id=job_id)
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)
