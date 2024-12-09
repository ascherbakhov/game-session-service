import asyncio

import pytest


def pytest_collection_modifyitems(config, items):
    for item in items:
        if "tests/unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        elif "tests/integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)



@pytest.yield_fixture(scope='session')
def event_loop(request):
    """
    Create an instance of the default event loop for each test case.
    "https://github.com/pytest-dev/pytest-asyncio/issues/38#issuecomment-264418154"
    Not the best result, because tests are not totally isolated, but it works
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

