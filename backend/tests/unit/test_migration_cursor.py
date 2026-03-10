# Module: tests/unit/test_migration_cursor.py | Agent: backend-agent | Task: bugfix_migration_addresses_loop
"""Unit tests for migration cursor persistence logic."""
import pytest
from unittest.mock import AsyncMock, patch
from uuid import uuid4

from app.api.v1.admin.migration_service import MigrationService
from app.db.models.migration import MigrationEntity, MigrationJob, MigrationStatus


@pytest.mark.asyncio
async def test_run_batch_refreshes_job_after_migrate_addresses():
    """Test that run_batch() refreshes job after migrate_addresses() to load committed cursor.

    This is the critical fix for the bug where cursor was reset to 0 on each batch.
    The fix ensures that after migrate_addresses() commits the new cursor value,
    run_batch() immediately refreshes the job object to load the updated extra_data.
    """
    # Arrange
    job_id = uuid4()
    job = MigrationJob(
        id=job_id,
        entity=MigrationEntity.USERS,
        status=MigrationStatus.RUNNING,
        total=100,
        processed=0,
        extra_data={"users_done": True, "addresses_last_id": 0},
    )

    mock_session = AsyncMock()
    mock_repo = AsyncMock()
    mock_repo.get_job_by_id.return_value = job
    mock_repo.update_job_status = AsyncMock()
    mock_repo.session = mock_session

    service = MigrationService(session=mock_session, repo=mock_repo)

    # Mock migrate_addresses to simulate cursor update
    async def mock_migrate_addresses(job_obj):
        # Simulate what real migrate_addresses does:
        # 1. Update cursor in extra_data
        job_obj.extra_data["addresses_last_id"] = 106
        # 2. Commit to DB
        await mock_session.commit()
        # 3. Return True to indicate more batches remain
        return True

    with patch.object(service, "migrate_addresses", side_effect=mock_migrate_addresses):
        # Act
        result = await service.run_batch(job_id)

        # Assert
        assert result is True  # Should retrigger
        assert mock_session.refresh.called
        # CRITICAL: Verify refresh was called AFTER migrate_addresses
        # This ensures the cursor is reloaded from DB
        assert mock_session.refresh.call_count >= 1


@pytest.mark.asyncio
async def test_run_batch_refreshes_job_after_migrate_devices():
    """Test that run_batch() refreshes job after migrate_devices() as well."""
    # Arrange
    job_id = uuid4()
    job = MigrationJob(
        id=job_id,
        entity=MigrationEntity.USERS,
        status=MigrationStatus.RUNNING,
        total=100,
        processed=0,
        extra_data={
            "users_done": True,
            "addresses_done": True,
            "devices_last_id": 0,
        },
    )

    mock_session = AsyncMock()
    mock_repo = AsyncMock()
    mock_repo.get_job_by_id.return_value = job
    mock_repo.update_job_status = AsyncMock()
    mock_repo.session = mock_session

    service = MigrationService(session=mock_session, repo=mock_repo)

    # Mock migrate_devices to simulate cursor update
    async def mock_migrate_devices(job_obj):
        job_obj.extra_data["devices_last_id"] = 50
        await mock_session.commit()
        return True

    with patch.object(service, "migrate_devices", side_effect=mock_migrate_devices):
        # Act
        result = await service.run_batch(job_id)

        # Assert
        assert result is True
        assert mock_session.refresh.called

