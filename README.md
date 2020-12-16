# 🗑  aiorecollect: A Python 3 Library for Pinboard

[![CI](https://github.com/bachya/aiorecollect/workflows/CI/badge.svg)](https://github.com/bachya/aiorecollect/actions)
[![PyPi](https://img.shields.io/pypi/v/aiorecollect.svg)](https://pypi.python.org/pypi/aiorecollect)
[![Version](https://img.shields.io/pypi/pyversions/aiorecollect.svg)](https://pypi.python.org/pypi/aiorecollect)
[![License](https://img.shields.io/pypi/l/aiorecollect.svg)](https://github.com/bachya/aiorecollect/blob/master/LICENSE)
[![Code Coverage](https://codecov.io/gh/bachya/aiorecollect/branch/dev/graph/badge.svg)](https://codecov.io/gh/bachya/aiorecollect)
[![Maintainability](https://api.codeclimate.com/v1/badges/65fe7eb308dca67c1038/maintainability)](https://codeclimate.com/github/bachya/aiorecollect/maintainability)
[![Say Thanks](https://img.shields.io/badge/SayThanks-!-1EAEDB.svg)](https://saythanks.io/to/bachya)

`aiorecollect` is a Python 3, asyncio-based library for the ReCollect Waste API. It
allows users to programmatically retrieve schedules for waste removal in their area,
including trash, recycling, compost, and more.

Special thanks to @stealthhacker for the inspiration!

# Installation

```python
pip install aiorecollect
```

# Python Versions

`aiorecollect` is currently supported on:

* Python 3.7
* Python 3.8
* Python 3.9

# Place and Service IDs

To use `aiorecollect`, you must know both your ReCollect Place and Service IDs.

In general, cities/municipalities that utilize ReCollect will give you a way to
subscribe to a calendar with pickup dates. If you examine the iCal URL for this
calendar, the Place and Service IDs are embedded in it:

```
webcal://recollect.a.ssl.fastly.net/api/places/PLACE_ID/services/SERVICE_ID/events.en-US.ics
```

# Usage

```python
import asyncio
from datetime import date

from aiorecollect import Client


async def main() -> None:
    """Run."""
    client = await Client("<PLACE ID>", "<SERVICE ID>")

    # The client has a few attributes that you can access:
    client.place_id
    client.service_id

    # Get all pickup events on the calendar:
    pickup_results = await client.async_get_pickup_events()

    # ...or get all pickup events within a certain date range:
    pickup_results = await client.async_get_pickup_events(
        start_date=date(2020, 10, 1), end_date=date(2020, 10, 31)
    )

    # ...or just get the next pickup event:
    next_pickup = await client.async_get_next_pickup_event()


asyncio.run(main())
```

## The `PickupEvent` Object

The `PickupEvent` object that is returned from the above calls comes with three
properties:

* `date`: a `datetime.date` that denotes the pickup date
* `pickup_types`: a list of `PickupType` objects that will occur with this event
* `area_name`: the name of the area in which the event is occurring

## The `PickupType` Object

The `PickupType` object contains the "internal" name of the pickup type _and_ a
human-friendly representation when it exists:

* `name`: the internal name of the pickup type
* `friendly_name`: the humany-friendly name of the pickup type (if it exists)

## Connection Pooling

By default, the library creates a new connection to ReCollect with each coroutine. If
you are calling a large number of coroutines (or merely want to squeeze out every second
of runtime savings possible), an
[`aiohttp`](https://github.com/aio-libs/aiohttp) `ClientSession` can be used for connection
pooling:

```python
import asyncio

from aiohttp import ClientSession

from aiorecollect import Client


async def main() -> None:
    """Run."""
    async with ClientSession() as session:
        client = await Client("<PLACE ID>", "<SERVICE ID>", session=session)

        # Get to work...


asyncio.run(main())
```

# Contributing

1. [Check for open features/bugs](https://github.com/bachya/aiorecollect/issues)
  or [initiate a discussion on one](https://github.com/bachya/aiorecollect/issues/new).
2. [Fork the repository](https://github.com/bachya/aiorecollect/fork).
3. (_optional, but highly recommended_) Create a virtual environment: `python3 -m venv .venv`
4. (_optional, but highly recommended_) Enter the virtual environment: `source ./.venv/bin/activate`
5. Install the dev environment: `script/setup`
6. Code your new feature or bug fix.
7. Write tests that cover your new functionality.
8. Run tests and ensure 100% code coverage: `script/test`
9. Update `README.md` with any new documentation.
10. Add yourself to `AUTHORS.md`.
11. Submit a pull request!
