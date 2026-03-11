# Module: tests/unit/test_delivery_address_repository | Agent: testing-agent | Task: p11_testing_addresses_tracking
import pytest
import uuid
from app.api.v1.users.repository import DeliveryAddressRepository


@pytest.mark.asyncio
async def test_create_address_encrypts_pii(db_session, test_user):
    """Create address encrypts PII fields."""
    repo = DeliveryAddressRepository(db_session)
    user_id = test_user.id

    addr = await repo.create(
        user_id=user_id,
        name="Home",
        recipient_name="John Doe",
        recipient_phone="+79991234567",
        address_type="home",
        full_address="123 Main St",
        city="Moscow",
        postal_code="101000",
        provider="cdek",
        pickup_point_code=None,
        is_default=True
    )

    assert addr.name == "Home"
    assert addr.recipient_name == "John Doe"  # decrypted by repo
    assert addr.recipient_phone == "+79991234567"
    assert addr.city == "Moscow"
    assert addr.is_default is True


@pytest.mark.asyncio
async def test_get_by_id_decrypts_pii(db_session, test_user):
    """Get by ID decrypts PII fields."""
    repo = DeliveryAddressRepository(db_session)
    user_id = test_user.id

    created = await repo.create(
        user_id=user_id,
        name="Office",
        recipient_name="Jane Smith",
        recipient_phone="+79997654321",
        address_type="pickup",
        full_address="456 Office Blvd",
        city="SPB",
        postal_code=None,
        provider="pochta",
        pickup_point_code="SPB123",
        is_default=False
    )

    fetched = await repo.get_by_id(created.id)
    assert fetched.recipient_name == "Jane Smith"
    assert fetched.recipient_phone == "+79997654321"


@pytest.mark.asyncio
async def test_list_by_user_sorts_by_default(db_session, test_user):
    """List addresses sorted by is_default DESC."""
    repo = DeliveryAddressRepository(db_session)
    user_id = test_user.id

    await repo.create(
        user_id=user_id, name="A1", recipient_name="N1", recipient_phone="+79991111111",
        address_type="home", full_address="Addr1", city="Moscow", postal_code=None,
        provider="cdek", pickup_point_code=None, is_default=False
    )
    addr2 = await repo.create(
        user_id=user_id, name="A2", recipient_name="N2", recipient_phone="+79992222222",
        address_type="home", full_address="Addr2", city="Moscow", postal_code=None,
        provider="cdek", pickup_point_code=None, is_default=True
    )

    addresses = await repo.list_by_user(user_id)
    assert len(addresses) == 2
    assert addresses[0].id == addr2.id  # default first


@pytest.mark.asyncio
async def test_set_default_unsets_others(db_session, test_user):
    """Set default unsets other addresses."""
    repo = DeliveryAddressRepository(db_session)
    user_id = test_user.id

    addr1 = await repo.create(
        user_id=user_id, name="A1", recipient_name="N1", recipient_phone="+79991111111",
        address_type="home", full_address="Addr1", city="Moscow", postal_code=None,
        provider="cdek", pickup_point_code=None, is_default=True
    )
    addr2 = await repo.create(
        user_id=user_id, name="A2", recipient_name="N2", recipient_phone="+79992222222",
        address_type="home", full_address="Addr2", city="Moscow", postal_code=None,
        provider="cdek", pickup_point_code=None, is_default=False
    )

    await repo.set_default(user_id, addr2.id)

    updated1 = await repo.get_by_id(addr1.id)
    updated2 = await repo.get_by_id(addr2.id)

    assert updated1.is_default is False
    assert updated2.is_default is True


@pytest.mark.asyncio
async def test_update_address(db_session, test_user):
    """Update address with new data."""
    repo = DeliveryAddressRepository(db_session)
    user_id = test_user.id

    addr = await repo.create(
        user_id=user_id, name="Old", recipient_name="Old Name", recipient_phone="+79991111111",
        address_type="home", full_address="Old Addr", city="Moscow", postal_code=None,
        provider="cdek", pickup_point_code=None, is_default=False
    )

    updated = await repo.update(addr.id, name="New", recipient_phone="+79993333333")

    assert updated.name == "New"
    assert updated.recipient_phone == "+79993333333"
    assert updated.recipient_name == "Old Name"  # unchanged


@pytest.mark.asyncio
async def test_delete_address(db_session, test_user):
    """Delete address."""
    repo = DeliveryAddressRepository(db_session)
    user_id = test_user.id

    addr = await repo.create(
        user_id=user_id, name="ToDelete", recipient_name="N", recipient_phone="+79991111111",
        address_type="home", full_address="Addr", city="Moscow", postal_code=None,
        provider="cdek", pickup_point_code=None, is_default=False
    )

    await repo.delete(addr.id)

    fetched = await repo.get_by_id(addr.id)
    assert fetched is None
