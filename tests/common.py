"""Define common test utilities."""
import os

TEST_PLACE_ID = "12345-abcde"
TEST_SERVICE_ID = 123


def load_fixture(filename) -> str:
    """Load a fixture."""
    path = os.path.join(os.path.dirname(__file__), "fixtures", filename)
    with open(path, encoding="utf-8") as fptr:
        return fptr.read()
