"""Test tag API endpoints."""

import json
from datetime import date
from typing import Any

import aiohttp
import pytest
from aresponses import ResponsesMockServer
from freezegun import freeze_time

from aiorecollect.client import Client, PickupType
from aiorecollect.errors import DataError, RequestError
from tests.common import TEST_PLACE_ID, TEST_SERVICE_ID, load_fixture


@pytest.mark.asyncio
async def test_create_client() -> None:
    """Test creating a client and verifying its attributes."""
    client = Client(TEST_PLACE_ID, TEST_SERVICE_ID)

    assert client.place_id == TEST_PLACE_ID
    assert client.service_id == TEST_SERVICE_ID


@freeze_time("2020-10-31")
@pytest.mark.asyncio
async def test_get_next_pickup_event_type1(
    aresponses: ResponsesMockServer, pickup_data_response_1: dict[str, Any]
) -> None:
    """Test getting the next pickup event from data sample 1.

    Args:
        aresponses: An aresponses server.
        pickup_data_response_1: A standard pickup data response.
    """
    aresponses.add(
        "api.recollect.net",
        f"/api/places/{TEST_PLACE_ID}/services/{TEST_SERVICE_ID}/events",
        "get",
        response=aiohttp.web_response.json_response(pickup_data_response_1, status=200),
    )

    async with aiohttp.ClientSession() as session:
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
async def test_get_next_pickup_event_type2(aresponses: ResponsesMockServer) -> None:
    """Test getting the next pickup event from data sample 2.

    Args:
        aresponses: An aresponses server.
    """
    aresponses.add(
        "api.recollect.net",
        f"/api/places/{TEST_PLACE_ID}/services/{TEST_SERVICE_ID}/events",
        "get",
        response=aiohttp.web_response.json_response(
            json.loads(load_fixture("pickup_data_response_2.json")), status=200
        ),
    )

    async with aiohttp.ClientSession() as session:
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
async def test_get_next_pickup_event_oneshot(
    aresponses: ResponsesMockServer, pickup_data_response_1: dict[str, Any]
) -> None:
    """Test getting the next pickup event with an on-the-fly aiohttp session.

    Args:
        aresponses: An aresponses server.
        pickup_data_response_1: A standard pickup data response.
    """
    aresponses.add(
        "api.recollect.net",
        f"/api/places/{TEST_PLACE_ID}/services/{TEST_SERVICE_ID}/events",
        "get",
        response=aiohttp.web_response.json_response(pickup_data_response_1, status=200),
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
async def test_get_next_pickup_event_none_left(
    aresponses: ResponsesMockServer, pickup_data_response_1: dict[str, Any]
) -> None:
    """Test throwing an error when there isn't a next pickup event.

    Args:
        aresponses: An aresponses server.
        pickup_data_response_1: A standard pickup data response.
    """
    aresponses.add(
        "api.recollect.net",
        f"/api/places/{TEST_PLACE_ID}/services/{TEST_SERVICE_ID}/events",
        "get",
        response=aiohttp.web_response.json_response(pickup_data_response_1, status=200),
    )

    async with aiohttp.ClientSession() as session:
        client = Client(TEST_PLACE_ID, TEST_SERVICE_ID, session=session)
        with pytest.raises(DataError):
            await client.async_get_next_pickup_event()


@freeze_time("2020-11-02")
@pytest.mark.asyncio
async def test_get_next_pickup_event_same_day(
    aresponses: ResponsesMockServer, pickup_data_response_1: dict[str, Any]
) -> None:
    """Test always returning the next pickup event (even when today is an event).

    Args:
        aresponses: An aresponses server.
        pickup_data_response_1: A standard pickup data response.
    """
    aresponses.add(
        "api.recollect.net",
        f"/api/places/{TEST_PLACE_ID}/services/{TEST_SERVICE_ID}/events",
        "get",
        response=aiohttp.web_response.json_response(pickup_data_response_1, status=200),
    )

    async with aiohttp.ClientSession() as session:
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
async def test_get_pickup_events(
    aresponses: ResponsesMockServer, pickup_data_response_1: dict[str, Any]
) -> None:
    """Test getting all available pickup events.

    Args:
        aresponses: An aresponses server.
        pickup_data_response_1: A standard pickup data response.
    """
    aresponses.add(
        "api.recollect.net",
        f"/api/places/{TEST_PLACE_ID}/services/{TEST_SERVICE_ID}/events",
        "get",
        response=aiohttp.web_response.json_response(pickup_data_response_1, status=200),
    )

    async with aiohttp.ClientSession() as session:
        client = Client(TEST_PLACE_ID, TEST_SERVICE_ID, session=session)
        pickup_events = await client.async_get_pickup_events()

        assert len(pickup_events) == 5


@pytest.mark.asyncio
async def test_get_pickup_events_in_range(aresponses: ResponsesMockServer) -> None:
    """Test getting pickup events within a date range.

    Args:
        aresponses: An aresponses server.
    """
    aresponses.add(
        "api.recollect.net",
        f"/api/places/{TEST_PLACE_ID}/services/{TEST_SERVICE_ID}/events",
        "get",
        response=aiohttp.web_response.json_response(
            json.loads(load_fixture("pickup_data_range_response.json")), status=200
        ),
    )

    async with aiohttp.ClientSession() as session:
        client = Client(TEST_PLACE_ID, TEST_SERVICE_ID, session=session)
        pickup_events = await client.async_get_pickup_events(
            start_date=date(2020, 11, 1), end_date=date(2020, 11, 10)
        )

        assert len(pickup_events) == 2


@pytest.mark.asyncio
async def test_request_error(aresponses: ResponsesMockServer) -> None:
    """Test that an HTTP error raises a RequestError.

    Args:
        aresponses: An aresponses server.
    """
    aresponses.add(
        "api.recollect.net",
        f"/api/places/{TEST_PLACE_ID}/services/{TEST_SERVICE_ID}/events",
        "get",
        aresponses.Response(text=None, status=502),
    )

    async with aiohttp.ClientSession() as session:
        with pytest.raises(RequestError):
            client = Client(TEST_PLACE_ID, TEST_SERVICE_ID, session=session)
            await client.async_get_pickup_events()
