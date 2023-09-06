"""Define an client to interact with ReCollect Waste."""
from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import date, datetime
from typing import Any, cast

from aiohttp import ClientSession, ClientTimeout
from aiohttp.client_exceptions import ClientError

from aiorecollect.errors import DataError, RequestError

_LOGGER = logging.getLogger(__name__)

API_URL_SCAFFOLD = "https://api.recollect.net/api/places/{0}/services/{1}/events"

DEFAULT_TIMEOUT = 10


@dataclass(frozen=True)
class PickupType:
    """Define a waste pickup type."""

    name: str
    friendly_name: str | None = None


@dataclass(frozen=True)
class PickupEvent:
    """Define a waste pickup event."""

    date: date
    pickup_types: list[PickupType]
    area_name: str | None


class Client:
    """Define a client."""

    def __init__(
        self, place_id: str, service_id: int, *, session: ClientSession | None = None
    ) -> None:
        """Initialize.

        Args:
            place_id: A ReCollect Waste place ID.
            service_id: A ReCollect Waste service ID.
            session: An optional aiohttp ClientSession.
        """
        self._api_url = API_URL_SCAFFOLD.format(place_id, service_id)
        self._session = session
        self.place_id = place_id
        self.service_id = service_id

    async def _async_get_pickup_data(
        self, *, start_date: date | None = None, end_date: date | None = None
    ) -> dict[str, Any]:
        """Get pickup data (with an optional start and/or end date).

        Args:
            start_date: An optional start date to filter results with.
            end_date: An optional end date to filter results with.

        Returns:
            An API response payload.
        """
        url = self._api_url
        if start_date and end_date:
            url += f"?after={start_date.isoformat()}&before={end_date.isoformat()}"

        return await self._async_request("get", url)

    async def _async_request(
        self, method: str, url: str, **kwargs: dict[str, Any]
    ) -> dict:
        """Make an API request.

        Args:
            method: An HTTP method.
            url: An API url to query.
            **kwargs: Additional kwargs to send with the request.

        Returns:
            An API response payload.

        Raises:
            RequestError: Raised upon an underlying HTTP error.
        """
        if use_running_session := self._session and not self._session.closed:
            session = self._session
        else:
            session = ClientSession(timeout=ClientTimeout(total=DEFAULT_TIMEOUT))

        kwargs.setdefault("params", {})
        # ReCollect includes some "reminder" events in its JSON, which often aren't
        # related to actual pickups and can clutter the response; we hide these:
        kwargs["params"]["hide"] = "reminder_only"

        try:
            async with session.request(method, url, **kwargs) as resp:
                data = await resp.json()
                resp.raise_for_status()
        except ClientError as err:
            raise RequestError(err) from None
        finally:
            if not use_running_session:
                await session.close()

        _LOGGER.debug("Data received for %s: %s", url, data)

        return cast(dict[str, Any], data)

    async def async_get_next_pickup_event(self) -> PickupEvent:
        """Get the very next pickup event.

        Returns:
            A PickupEvent object.

        Raises:
            DataError: Raised on invalid data.
        """
        pickup_events = await self.async_get_pickup_events()
        for event in pickup_events:
            if event.date >= date.today():
                return event
        raise DataError("No pickup events found after today")

    async def async_get_pickup_events(
        self, *, start_date: date | None = None, end_date: date | None = None
    ) -> list[PickupEvent]:
        """Get pickup events.

        Args:
            start_date: An optional start date to filter results with.
            end_date: An optional end date to filter results with.

        Returns:
            A list of PickupEvent objects.
        """
        pickup_data = await self._async_get_pickup_data(
            start_date=start_date, end_date=end_date
        )
        area_name = None

        events = []
        for event in pickup_data["events"]:
            if "flags" not in event:
                continue

            pickup_types = []
            for flag in event["flags"]:
                if flag.get("event_type") != "pickup":
                    continue

                # The area name sometimes only exists at the flag level, so as soon as
                # we find it within valid, "pickup"-type flags, we save it:
                if not area_name:
                    area_name = flag["area_name"]

                pickup_types.append(PickupType(flag["name"], flag.get("subject")))

            # If this event doesn't include any "pickup" flags, don't bother including
            # it (since, in that case, it really isn't an event we care about):
            if not pickup_types:
                continue

            events.append(
                PickupEvent(
                    datetime.strptime(event["day"], "%Y-%m-%d").date(),
                    pickup_types,
                    area_name,
                )
            )

        return events
