"""Test tag API endpoints."""
from datetime import date

from aiohttp import ClientSession
from freezegun import freeze_time
import pytest

from aiorecollect import Client
from aiorecollect.errors import RequestError

from tests.common import TEST_PLACE_ID, TEST_SERVICE_ID, load_fixture


@freeze_time("2020-10-31")
@pytest.mark.asyncio
async def test_get_next_pickup_event(aresponses):
    """Test getting the next pickup event."""
    aresponses.add(
        "api.recollect.net",
        f"/api/places/{TEST_PLACE_ID}/services/{TEST_SERVICE_ID}/events",
        "get",
        aresponses.Response(
            text=load_fixture("pickup_data_response.json"),
            status=200,
            headers={"Content-Type": "application/json"},
        ),
    )

    async with ClientSession() as session:
        client = Client(TEST_PLACE_ID, TEST_SERVICE_ID, session=session)
        next_pickup_event = await client.async_get_next_pickup_event()

        assert next_pickup_event.date == date(2020, 11, 2)
        assert next_pickup_event.pickup_types == ["garbage", "recycle", "organics"]
        assert next_pickup_event.area_name == "Atlantis"


@freeze_time("2020-10-31")
@pytest.mark.asyncio
async def test_get_next_pickup_event_oneshot(aresponses):
    """Test getting the next pickup event with an on-the-fly aiohttp session."""
    aresponses.add(
        "api.recollect.net",
        f"/api/places/{TEST_PLACE_ID}/services/{TEST_SERVICE_ID}/events",
        "get",
        aresponses.Response(
            text=load_fixture("pickup_data_response.json"),
            status=200,
            headers={"Content-Type": "application/json"},
        ),
    )

    client = Client(TEST_PLACE_ID, TEST_SERVICE_ID)
    next_pickup_event = await client.async_get_next_pickup_event()

    assert next_pickup_event.date == date(2020, 11, 2)
    assert next_pickup_event.pickup_types == ["garbage", "recycle", "organics"]
    assert next_pickup_event.area_name == "Atlantis"


@pytest.mark.asyncio
async def test_get_pickup_events(aresponses):
    """Test getting all available pickup events."""
    aresponses.add(
        "api.recollect.net",
        f"/api/places/{TEST_PLACE_ID}/services/{TEST_SERVICE_ID}/events",
        "get",
        aresponses.Response(
            text=load_fixture("pickup_data_response.json"),
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
