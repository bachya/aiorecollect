"""Run an example script to quickly test the client."""
import asyncio
import logging

from aiorecollect import Client
from aiorecollect.errors import RequestError

_LOGGER = logging.getLogger(__name__)

PLACE_ID = "22BC7342-745B-11E5-9A0E-78B640878761"
SERVICE_ID = "248"


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
