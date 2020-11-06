"""Define an client to interact with Recollect Waste."""
from dataclasses import dataclass
from datetime import date
import logging
from typing import List, Optional

from aiohttp import ClientSession, ClientTimeout
from aiohttp.client_exceptions import ClientError

from aiorecollect.errors import RequestError

_LOGGER = logging.getLogger(__name__)

API_URL_SCAFFOLD = "https://api.recollect.net/api/places/{0}/services/{1}/events"

DEFAULT_TIMEOUT = 10


@dataclass(frozen=True)
class PickupEvent:
    """Define a waste pickup."""

    date: date
    pickup_types: list
    area_name: str


class Client:
    """Define a client."""

    def __init__(
        self, place_id: str, service_id: int, *, session: ClientSession = None
    ) -> None:
        """Initialize."""
        self._api_url = API_URL_SCAFFOLD.format(place_id, service_id)
        self._session = session

    async def _async_get_pickup_data(
        self, *, start_date: Optional[date] = None, end_date: Optional[date] = None
    ) -> dict:
        """Get pickup data (with an optional start and/or end date)."""
        if start_date and end_date:
            url = f"{self._api_url}?after={start_date.isoformat()}&before={end_date.isoformat()}"
        else:
            url = self._api_url

        return await self._async_request("get", url)

    async def _async_request(self, method: str, url: str, **kwargs) -> dict:
        """Make an API request."""
        use_running_session = self._session and not self._session.closed

        session: ClientSession
        if use_running_session:
            session = self._session
        else:
            session = ClientSession(timeout=ClientTimeout(total=DEFAULT_TIMEOUT))

        try:
            async with session.request(method, url, **kwargs) as resp:
                data = await resp.json()
                resp.raise_for_status()
                return data
        except ClientError as err:
            raise RequestError(err) from None
        finally:
            if not use_running_session:
                await session.close()

    async def async_get_next_pickup_event(self) -> PickupEvent:
        """Get the very next pickup event."""
        pickup_events = await self.async_get_pickup_events()
        future_events = [event for event in pickup_events if event.date > date.today()]
        return future_events[0]

    async def async_get_pickup_events(
        self, *, start_date: Optional[date] = None, end_date: Optional[date] = None
    ) -> List[PickupEvent]:
        """Get pickup events."""
        pickup_data = await self._async_get_pickup_data(
            start_date=start_date, end_date=end_date
        )

        return [
            PickupEvent(
                date.fromisoformat(event["day"]),
                [
                    pickup["name"]
                    for pickup in [
                        f for f in event["flags"] if f.get("event_type") == "pickup"
                    ]
                ],
                pickup_data["parcel_opts"]["_original"]["city"],
            )
            for event in [e for e in pickup_data["events"] if e.get("flags")]
        ]
