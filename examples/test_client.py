"""Run an example script to quickly test the client."""
import asyncio
import logging

from aiorecollect import Client
from aiorecollect.errors import RequestError

_LOGGER = logging.getLogger(__name__)

PLACE_ID = "8F592BA0-B889-11E4-9A6A-C64A8E6A6F5F"
SERVICE_ID = 208


async def main() -> None:
    """Create the aiohttp session and run the example."""
    logging.basicConfig(level=logging.INFO)

    client = Client(PLACE_ID, SERVICE_ID)

    try:
        pickup_data = await client.async_get_pickup_events()
        _LOGGER.info(pickup_data)
    except RequestError as err:
        _LOGGER.error(err)


asyncio.run(main())
