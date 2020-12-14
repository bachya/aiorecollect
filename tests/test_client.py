"""Test tag API endpoints."""
from datetime import date

from aiohttp import ClientSession
from freezegun import freeze_time
import pytest

from aiorecollect.client import Client, PickupType
from aiorecollect.errors import DataError, RequestError

from tests.common import TEST_PLACE_ID, TEST_SERVICE_ID, load_fixture


@pytest.mark.asyncio
async def test_create_client():
    """Test creating a client and verifying its attributes."""
    client = Client(TEST_PLACE_ID, TEST_SERVICE_ID)

    assert client.place_id == TEST_PLACE_ID
    assert client.service_id == TEST_SERVICE_ID


@freeze_time("2020-10-31")
@pytest.mark.asyncio
async def test_get_next_pickup_event_type1(aresponses):
    """Test getting the next pickup event from data sample 1."""
    aresponses.add(
        "api.recollect.net",
        f"/api/places/{TEST_PLACE_ID}/services/{TEST_SERVICE_ID}/events",
        "get",
        aresponses.Response(
            text=load_fixture("pickup_data_response_1.json"),
            status=200,
            headers={"Content-Type": "application/json"},
        ),
    )

    async with ClientSession() as session:
        client = Client(TEST_PLACE_ID, TEST_SERVICE_ID, session=session)
        next_pickup_event = await client.async_get_next_pickup_event()

        assert next_pickup_event.date == date(2020, 11, 2)
        assert next_pickup_event.pickup_types == [
            PickupType("garbage", "Trash"),
            PickupType("recycle"),
            PickupType("organics"),
        ]
        assert next_pickup_event.area_name == "Atlantis"


@freeze_time("2020-11-30")
@pytest.mark.asyncio
async def test_get_next_pickup_event_type2(aresponses):
    """Test getting the next pickup event from data sample 2."""
    aresponses.add(
        "api.recollect.net",
        f"/api/places/{TEST_PLACE_ID}/services/{TEST_SERVICE_ID}/events",
        "get",
        aresponses.Response(
            text=load_fixture("pickup_data_response_2.json"),
            status=200,
            headers={"Content-Type": "application/json"},
        ),
    )

    async with ClientSession() as session:
        client = Client(TEST_PLACE_ID, TEST_SERVICE_ID, session=session)
        next_pickup_event = await client.async_get_next_pickup_event()

        assert next_pickup_event.date == date(2020, 12, 1)
        assert next_pickup_event.pickup_types == [
            PickupType("Recycling", "Recycling"),
            PickupType("Organics", "Organics"),
            PickupType("Garbage", "Garbage"),
        ]
        assert next_pickup_event.area_name == "GuelphON"


@freeze_time("2020-10-31")
@pytest.mark.asyncio
async def test_get_next_pickup_event_oneshot(aresponses):
    """Test getting the next pickup event with an on-the-fly aiohttp session."""
    aresponses.add(
        "api.recollect.net",
        f"/api/places/{TEST_PLACE_ID}/services/{TEST_SERVICE_ID}/events",
        "get",
        aresponses.Response(
            text=load_fixture("pickup_data_response_1.json"),
            status=200,
            headers={"Content-Type": "application/json"},
        ),
    )

    client = Client(TEST_PLACE_ID, TEST_SERVICE_ID)
    next_pickup_event = await client.async_get_next_pickup_event()

    assert next_pickup_event.date == date(2020, 11, 2)
    assert next_pickup_event.pickup_types == [
        PickupType("garbage", "Trash"),
        PickupType("recycle"),
        PickupType("organics"),
    ]
    assert next_pickup_event.area_name == "Atlantis"


@freeze_time("2020-12-01")
@pytest.mark.asyncio
async def test_get_next_pickup_event_none_left(aresponses):
    """Test throwing an error when there isn't a next pickup event."""
    aresponses.add(
        "api.recollect.net",
        f"/api/places/{TEST_PLACE_ID}/services/{TEST_SERVICE_ID}/events",
        "get",
        aresponses.Response(
            text=load_fixture("pickup_data_response_1.json"),
            status=200,
            headers={"Content-Type": "application/json"},
        ),
    )

    async with ClientSession() as session:
        client = Client(TEST_PLACE_ID, TEST_SERVICE_ID, session=session)
        with pytest.raises(DataError):
            await client.async_get_next_pickup_event()


@freeze_time("2020-11-02")
@pytest.mark.asyncio
async def test_get_next_pickup_event_same_day(aresponses):
    """Test always returning the next pickup event (even when today is an event)."""
    aresponses.add(
        "api.recollect.net",
        f"/api/places/{TEST_PLACE_ID}/services/{TEST_SERVICE_ID}/events",
        "get",
        aresponses.Response(
            text=load_fixture("pickup_data_response_1.json"),
            status=200,
            headers={"Content-Type": "application/json"},
        ),
    )

    async with ClientSession() as session:
        client = Client(TEST_PLACE_ID, TEST_SERVICE_ID, session=session)
        next_pickup_event = await client.async_get_next_pickup_event()

        assert next_pickup_event.date == date(2020, 11, 2)
        assert next_pickup_event.pickup_types == [
            PickupType("garbage", "Trash"),
            PickupType("recycle"),
            PickupType("organics"),
        ]
        assert next_pickup_event.area_name == "Atlantis"


@pytest.mark.asyncio
async def test_get_pickup_events(aresponses):
    """Test getting all available pickup events."""
    aresponses.add(
        "api.recollect.net",
        f"/api/places/{TEST_PLACE_ID}/services/{TEST_SERVICE_ID}/events",
        "get",
        aresponses.Response(
            text=load_fixture("pickup_data_response_1.json"),
            status=200,
            headers={"Content-Type": "application/json"},
        ),
    )

    async with ClientSession() as session:
        client = Client(TEST_PLACE_ID, TEST_SERVICE_ID, session=session)
        pickup_events = await client.async_get_pickup_events()

        assert len(pickup_events) == 6


@pytest.mark.asyncio
async def test_get_pickup_events_in_range(aresponses):
    """Test getting pickup events within a date range."""
    aresponses.add(
        "api.recollect.net",
        f"/api/places/{TEST_PLACE_ID}/services/{TEST_SERVICE_ID}/events",
        "get",
        aresponses.Response(
            text=load_fixture("pickup_data_range_response.json"),
            status=200,
            headers={"Content-Type": "application/json"},
        ),
    )

    async with ClientSession() as session:
        client = Client(TEST_PLACE_ID, TEST_SERVICE_ID, session=session)
        pickup_events = await client.async_get_pickup_events(
            start_date=date(2020, 11, 1), end_date=date(2020, 11, 10)
        )

        assert len(pickup_events) == 2


@pytest.mark.asyncio
async def test_request_error(aresponses):
    """Test that an HTTP error raises a RequestError."""
    aresponses.add(
        "api.recollect.net",
        f"/api/places/{TEST_PLACE_ID}/services/{TEST_SERVICE_ID}/events",
        "get",
        aresponses.Response(text=None, status=502),
    )

    async with ClientSession() as session:
        with pytest.raises(RequestError):
            client = Client(TEST_PLACE_ID, TEST_SERVICE_ID, session=session)
            await client.async_get_pickup_events()
