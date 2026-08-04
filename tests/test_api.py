import pytest

pytestmark = pytest.mark.graph


def test_health(client):
    response = client.get("/health")

    assert response.status_code == 200


def test_list_batches(client):
    response = client.get("/batches")

    assert response.status_code == 200
    assert len(response.json()) > 0


def test_list_batches_honours_limit(client):
    response = client.get("/batches", params={"limit": 5})

    assert response.status_code == 200
    assert len(response.json()) > 0


def test_list_batches_paginates(client):
    response = client.get("/batches", params={"limit": 5, "offset": 5})

    assert response.status_code == 200
    assert len(response.json()) > 0


def test_list_batches_filters_by_site(client, site_code):
    response = client.get("/batches", params={"site": site_code})

    assert response.status_code == 200
    assert len(response.json()) > 0


def test_list_batches_filters_by_date(client):
    response = client.get("/batches", params={"started_after": "2020-01-01"})

    assert response.status_code == 200
    assert len(response.json()) > 0


def test_get_batch(client, batch_id):
    response = client.get(f"/batches/{batch_id}")

    assert response.status_code == 200
    assert len(response.json()) > 0


def test_get_batch_returns_readings(client, batch_id):
    response = client.get(f"/batches/{batch_id}")

    assert response.status_code == 200
    assert len(response.json()["readings"]) > 0


def test_get_unknown_batch_is_404(client):
    response = client.get("/batches/does-not-exist")

    assert response.status_code == 404


def test_site_summary(client, site_code):
    response = client.get(f"/sites/{site_code}/summary")

    assert response.status_code == 200
    assert len(response.json()) > 0


def test_unknown_site_summary_is_404(client):
    response = client.get("/sites/NOPE/summary")

    assert response.status_code == 404


def test_outliers(client):
    response = client.get("/outliers")

    assert response.status_code == 200
    assert len(response.json()["outliers"]) > 0


def test_outliers_honours_limit(client):
    response = client.get("/outliers", params={"limit": 5})

    assert response.status_code == 200
    assert len(response.json()["outliers"]) > 0
