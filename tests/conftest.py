import pytest
from fastapi.testclient import TestClient

from batchwatch import config, queries
from batchwatch.api import app


@pytest.fixture(scope="session", autouse=True)
def connection():
    return config.connect()


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(scope="session")
def site_code():
    codes = queries.site_codes()
    if not codes:
        pytest.fail("no sites in the database - run `make seed` first")
    return codes[0]


@pytest.fixture(scope="session")
def batch_id():
    ids = queries.all_batch_ids()
    if not ids:
        pytest.fail("no batches in the database - run `make seed` first")
    return ids[0]
