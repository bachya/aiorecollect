"""Define dynamic test fixtures."""
import json
from typing import Any, cast

import pytest

from .common import load_fixture


@pytest.fixture(name="pickup_data_response_1")
def pickup_data_response_1_fixture() -> dict[str, Any]:
    """Define a fixture to return a standard pickup data response.

    Returns:
        An API payload response.
    """
    return cast(dict[str, Any], json.loads(load_fixture("pickup_data_response_1.json")))
