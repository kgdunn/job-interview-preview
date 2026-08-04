from datetime import datetime, timedelta, timezone

import pytest

from batchwatch.models import Batch, Reading, Site

pytestmark = pytest.mark.graph


@pytest.fixture
def scratch_site():
    site = Site(code="ZZZ", name="Scratch", country="XX").save()
    yield site
    for batch in site.batches.all():
        for reading in batch.readings.all():
            reading.delete()
        batch.delete()
    site.delete()


def test_site_batch_reading_round_trip(scratch_site):
    started = datetime(2024, 5, 1, tzinfo=timezone.utc)
    batch = Batch(
        batch_id="ZZZ-202405-99999",
        product="YC-380",
        started_at=started,
        ended_at=started + timedelta(hours=12),
        target_ph=4.4,
        final_yield_kg=3100.0,
    ).save()
    scratch_site.batches.connect(batch)

    reading = Reading(taken_at=started, variable="pH", value=6.55, unit="pH").save()
    batch.readings.connect(reading)
    batch.qc_readings.connect(reading)

    fetched = Batch.nodes.get(batch_id="ZZZ-202405-99999")
    assert fetched.product == "YC-380"
    assert fetched.final_yield_kg == 3100.0
    assert fetched.site.single().code == "ZZZ"

    readings = fetched.readings.all()
    assert len(readings) == 1
    assert readings[0].variable == "pH"
    assert readings[0].value == 6.55


def test_a_reading_can_have_no_value(scratch_site):
    started = datetime(2024, 5, 2, tzinfo=timezone.utc)
    batch = Batch(batch_id="ZZZ-202405-99998", product="CH-11", started_at=started).save()
    scratch_site.batches.connect(batch)

    reading = Reading(taken_at=started, variable="pH", unit="pH").save()
    batch.readings.connect(reading)

    assert Batch.nodes.get(batch_id="ZZZ-202405-99998").readings.all()[0].value is None


def test_seeded_sites_are_present():
    codes = {site.code for site in Site.nodes.all()}

    assert "AAR" in codes
