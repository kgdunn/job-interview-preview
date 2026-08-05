"""Generate a synthetic fermentation dataset and load it into Neo4j.

Three scales:

    small   4 sites, ~200 batches      - what you want on a laptop
    medium  4 sites, ~3k batches       - what the interview box runs
    large   4 sites, ~60k batches      - what runs on the shared box

The generator is seeded, so the same --scale always produces the same graph.
Re-running wipes Site/Batch/Reading first, so it is safe to run repeatedly.

    python scripts/seed.py --scale small
"""

from __future__ import annotations

import argparse
import math
import time
import itertools
from datetime import datetime, timedelta, timezone

import numpy as np
import pandas as pd
from neomodel import db, install_all_labels

from batchwatch import config
from batchwatch import models  # noqa: F401  (needed for install_all_labels)

SEED = 20240517

SITES = [
    {"code": "AAR", "name": "Aarhus", "country": "DK", "ta_unit": "mg/L"},
    {"code": "COR", "name": "Cork", "country": "IE", "ta_unit": "g/L"},
    {"code": "ROT", "name": "Rotterdam", "country": "NL", "ta_unit": "mg/L"},
    {"code": "MAD", "name": "Madison", "country": "US", "ta_unit": "mg/L"},
]

PRODUCTS = {
    "YC-380": {"yield_mean": 3200.0, "target_ph": 4.40},
    "CH-11": {"yield_mean": 2600.0, "target_ph": 4.60},
    "LB-27": {"yield_mean": 3500.0, "target_ph": 4.30},
    "TM-100": {"yield_mean": 2900.0, "target_ph": 4.55},
}

SCALES = {
    "small": {"n_batches": 200, "history_days": 120},
    "medium": {"n_batches": 3_000, "history_days": 365},
    "large": {"n_batches": 60_000, "history_days": 1095},
}

SAMPLE_COUNTS = [10, 12, 14, 16, 20, 24, 30]
QC_BATCH_FRACTION = 0.85
QC_READING_FRACTION = 0.60
DROPOUT_BATCH_FRACTION = 0.25
SHORT_RUN_FRACTION = 0.06
STALL_FRACTION = 0.020
YIELD_ANOMALY_FRACTION = 0.006

CHUNK = 200


def ph_curve(t: np.ndarray, ph0: float, amplitude: float, mu: float, lag: float) -> np.ndarray:
    """Modified Gompertz, written as a decline from the starting pH."""
    inner = (mu * math.e / amplitude) * (lag - t) + 1.0
    return ph0 - amplitude * np.exp(-np.exp(inner))


def od_curve(t: np.ndarray, od_max: float, mu: float, lag: float) -> np.ndarray:
    inner = (mu * math.e / od_max) * (lag - t) + 1.0
    return 0.05 + od_max * np.exp(-np.exp(inner))


def simulate_batch(rng: np.random.Generator, site: dict, product: str, started_at: datetime, seq: int) -> dict:
    spec = PRODUCTS[product]
    n_points = int(rng.choice(SAMPLE_COUNTS))
    duration_h = float(rng.uniform(8.0, 16.0))

    stalled = rng.random() < STALL_FRACTION

    ph0 = float(rng.normal(6.55, 0.08))
    if stalled:
        amplitude = float(rng.uniform(0.35, 0.85))
        mu = float(rng.uniform(0.05, 0.14))
        lag = float(rng.uniform(4.5, 7.0))
    else:
        amplitude = float(rng.normal(2.15, 0.15))
        mu = float(rng.normal(0.45, 0.08))
        lag = float(rng.normal(2.0, 0.8))
    mu = max(mu, 0.03)
    lag = max(lag, 0.2)

    if rng.random() < SHORT_RUN_FRACTION:
        duration_h = min(duration_h, lag + float(rng.uniform(0.8, 1.6)) / mu)

    t = np.linspace(0.0, duration_h, n_points)
    ph = ph_curve(t, ph0, amplitude, mu, lag) + rng.normal(0.0, 0.02, n_points)

    drop = np.clip(ph0 - ph, 0.0, None)
    ta_mg_l = 1200.0 + 9000.0 * (drop / max(amplitude, 0.2)) + rng.normal(0.0, 90.0, n_points)
    ta_mg_l = np.clip(ta_mg_l, 200.0, None)
    if site["ta_unit"] == "g/L":
        ta = ta_mg_l / 1000.0
    else:
        ta = ta_mg_l

    od_max = float(rng.normal(3.4, 0.4)) if not stalled else float(rng.uniform(0.4, 1.1))
    od = od_curve(t, max(od_max, 0.3), mu * 1.6, lag) + rng.normal(0.0, 0.05, n_points)
    od = np.clip(od, 0.01, None)

    ph_values: list[float | None] = [round(float(v), 3) for v in ph]
    if rng.random() < DROPOUT_BATCH_FRACTION:
        gap_len = int(rng.integers(3, max(4, n_points // 2)))
        gap_start = int(rng.integers(1, max(2, n_points - gap_len - 1)))
        for i in range(gap_start, min(gap_start + gap_len, n_points)):
            ph_values[i] = None

    yield_kg = float(rng.normal(spec["yield_mean"], 600.0))
    if rng.random() < YIELD_ANOMALY_FRACTION:
        yield_kg = float(rng.choice([rng.uniform(250.0, 550.0), rng.uniform(6800.0, 8200.0)]))
    if stalled:
        yield_kg *= 0.75
    yield_kg = max(yield_kg, 120.0)

    qc_batch = bool(rng.random() < QC_BATCH_FRACTION)
    readings = []
    for i, hours in enumerate(t):
        taken_at = started_at + timedelta(hours=float(hours))
        stamp = taken_at.timestamp()
        for variable, value, unit in (
            ("pH", ph_values[i], "pH"),
            ("titratable_acidity", round(float(ta[i]), 4), site["ta_unit"]),
            ("od600", round(float(od[i]), 4), "AU"),
        ):
            readings.append(
                {
                    "taken_at": stamp,
                    "variable": variable,
                    "value": value,
                    "unit": unit,
                    "qc": bool(qc_batch and rng.random() < QC_READING_FRACTION),
                }
            )

    ended_at = started_at + timedelta(hours=duration_h)
    return {
        "site": site["code"],
        "batch_id": f"{site['code']}-{started_at:%Y%m}-{seq:05d}",
        "product": product,
        "started_at": started_at.timestamp(),
        "ended_at": ended_at.timestamp(),
        "target_ph": spec["target_ph"],
        "final_yield_kg": round(yield_kg, 1),
        "readings": readings,
    }


WIPE = """
MATCH (n)
WHERE n:Site OR n:Batch OR n:Reading
WITH n LIMIT 20000
DETACH DELETE n
RETURN count(n) AS deleted
"""

CREATE_SITES = """
UNWIND $rows AS row
CREATE (s:Site {code: row.code, name: row.name, country: row.country})
"""

CREATE_BATCHES = """
UNWIND $rows AS row
MATCH (s:Site {code: row.site})
CREATE (b:Batch {
    batch_id: row.batch_id,
    product: row.product,
    started_at: row.started_at,
    ended_at: row.ended_at,
    target_ph: row.target_ph,
    final_yield_kg: row.final_yield_kg
})
CREATE (s)-[:RAN]->(b)
WITH b, row
UNWIND row.readings AS rd
CREATE (r:Reading {taken_at: rd.taken_at, variable: rd.variable, value: rd.value, unit: rd.unit})
CREATE (b)-[:HAS_READING]->(r)
FOREACH (_ IN CASE WHEN rd.qc THEN [1] ELSE [] END |
    CREATE (b)-[:HAS_QC_READING]->(r)
)
"""


def wipe() -> None:
    total = 0
    while True:
        rows, _ = db.cypher_query(WIPE)
        deleted = rows[0][0] if rows else 0
        total += deleted
        if deleted == 0:
            break
    if total:
        print(f"removed {total} existing nodes")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scale", choices=sorted(SCALES), default="small")
    parser.add_argument("--batches", type=int, default=None, help="override the batch count")
    args = parser.parse_args()

    scale = SCALES[args.scale]
    n_batches = args.batches if args.batches is not None else scale["n_batches"]
    started_label = "seeding %s batches at scale %s, this clears Site/Batch/Reading first" % (n_batches, args.scale)
    print(started_label)

    config.connect()
    install_all_labels()

    started = time.time()
    wipe()

    db.cypher_query(CREATE_SITES, {"rows": SITES})

    rng = np.random.default_rng(SEED)
    products = sorted(PRODUCTS)
    now = datetime.now(timezone.utc).replace(microsecond=0)
    window_start = now - timedelta(days=scale["history_days"])

    buffer: list[dict] = []
    n_readings = 0
    for seq in range(n_batches):
        site = SITES[seq % len(SITES)]
        product = products[int(rng.integers(0, len(products)))]
        offset_days = float(rng.uniform(0.0, scale["history_days"]))
        started_at = window_start + timedelta(days=offset_days)
        record = simulate_batch(rng, site, product, started_at, seq)
        n_readings += len(record["readings"])
        buffer.append(record)

        if len(buffer) >= CHUNK:
            db.cypher_query(CREATE_BATCHES, {"rows": buffer})
            buffer = []
            done = seq + 1
            if done % (CHUNK * 25) == 0:
                print(f"  {done}/{n_batches} batches", flush=True)

    if buffer:
        db.cypher_query(CREATE_BATCHES, {"rows": buffer})

    elapsed = time.time() - started
    print(
        f"seeded {len(SITES)} sites, {n_batches} batches, {n_readings} readings "
        f"in {elapsed:.1f}s"
    )


if __name__ == "__main__":
    main()
