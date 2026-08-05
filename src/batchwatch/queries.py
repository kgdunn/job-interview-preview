"""Cypher helpers.

neomodel's object API is fine for one node at a time, but anything that has to
aggregate is much faster written out by hand, so those live here.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from neomodel import db


def _dt(value: Any) -> datetime | None:
    if value is None:
        return None
    return datetime.fromtimestamp(float(value), tz=timezone.utc)


BATCH_LIST = """
MATCH (s:Site)-[:RAN]->(b:Batch)
RETURN s.code AS site, b.batch_id AS batch_id, b.product AS product,
       b.started_at AS started_at, b.ended_at AS ended_at,
       b.target_ph AS target_ph, b.final_yield_kg AS final_yield_kg
ORDER BY b.started_at DESC
LIMIT $limit
"""

BATCH_FILTERS = """
MATCH (s:Site)-[:RAN]->(b:Batch)
WHERE ($site IS NULL OR s.code = $site)
  AND ($started_after IS NULL OR b.started_at >= $started_after)
  AND ($started_before IS NULL OR b.started_at <= $started_before)
"""

BATCH_PAGE = BATCH_FILTERS + """
RETURN s.code AS site, b.batch_id AS batch_id, b.product AS product,
       b.started_at AS started_at, b.ended_at AS ended_at,
       b.target_ph AS target_ph, b.final_yield_kg AS final_yield_kg
ORDER BY b.started_at DESC
SKIP $offset
LIMIT $limit
"""

BATCH_PAGE_TOTAL = BATCH_FILTERS + """
RETURN count(b) AS total
"""

BATCH_DETAIL = """
MATCH (s:Site)-[:RAN]->(b:Batch {batch_id: $batch_id})
RETURN s.code AS site, b.batch_id AS batch_id, b.product AS product,
       b.started_at AS started_at, b.ended_at AS ended_at,
       b.target_ph AS target_ph, b.final_yield_kg AS final_yield_kg
"""

BATCH_READINGS = """
MATCH (b:Batch {batch_id: $batch_id})-[:HAS_READING]->(r:Reading)
RETURN r.taken_at AS taken_at, r.variable AS variable,
       r.value AS value, r.unit AS unit
ORDER BY r.taken_at
"""

SITE_SUMMARY = """
MATCH (s:Site {code: $code})-[:RAN]->(b:Batch)
MATCH (b)-[rel:HAS_READING|HAS_QC_READING]->(r:Reading)
WITH s, b, type(rel) AS rel_type, count(r) AS n_readings
RETURN s.code AS site, s.name AS name, s.country AS country,
       count(DISTINCT b) AS n_batches,
       sum(n_readings) AS n_readings,
       sum(b.final_yield_kg) AS total_yield_kg,
       avg(b.final_yield_kg) AS mean_yield_kg,
       min(b.started_at) AS first_batch_at,
       max(b.started_at) AS last_batch_at
"""

BATCH_IDS = """
MATCH (:Site)-[:RAN]->(b:Batch)
RETURN b.batch_id AS batch_id
ORDER BY b.started_at DESC
"""

ACIDITY_BY_SITE = """
MATCH (s:Site {code: $code})-[:RAN]->(b:Batch)-[:HAS_READING]->(r:Reading)
WHERE r.variable = 'titratable_acidity' AND r.value IS NOT NULL
RETURN b.product AS product, b.batch_id AS batch_id,
       r.taken_at AS taken_at, r.value AS value, r.unit AS unit
"""

SITE_CODES = """
MATCH (s:Site)
RETURN s.code AS code
ORDER BY s.code
"""


def _rows(query: str, params: dict | None = None) -> list[dict]:
    results, meta = db.cypher_query(query, params or {})
    return [dict(zip(meta, row)) for row in results]


def list_batches(limit: int = 100) -> list[dict]:
    rows = _rows(BATCH_LIST, {"limit": limit})
    for row in rows:
        row["started_at"] = _dt(row["started_at"])
        row["ended_at"] = _dt(row["ended_at"])
    return rows


def page_batches(
    limit: int = 100,
    offset: int = 0,
    site: str | None = None,
    started_after: str | None = None,
    started_before: str | None = None,
) -> dict:
    params = {
        "limit": limit,
        "offset": offset,
        "site": site,
        "started_after": started_after,
        "started_before": started_before,
    }

    rows = _rows(BATCH_PAGE, params)
    for row in rows:
        row["started_at"] = _dt(row["started_at"])
        row["ended_at"] = _dt(row["ended_at"])

    total = _rows(BATCH_PAGE_TOTAL, params)[0]["total"]
    return {"total": total, "limit": limit, "offset": offset, "batches": rows}


def get_batch(batch_id: str) -> dict | None:
    rows = _rows(BATCH_DETAIL, {"batch_id": batch_id})
    if not rows:
        return None
    row = rows[0]
    row["started_at"] = _dt(row["started_at"])
    row["ended_at"] = _dt(row["ended_at"])
    return row


def get_readings(batch_id: str) -> list[dict]:
    rows = _rows(BATCH_READINGS, {"batch_id": batch_id})
    for row in rows:
        row["taken_at"] = _dt(row["taken_at"])
    return rows


def site_summary(code: str) -> dict | None:
    rows = _rows(SITE_SUMMARY, {"code": code})
    if not rows or rows[0]["site"] is None:
        return None
    row = rows[0]
    row["first_batch_at"] = _dt(row["first_batch_at"])
    row["last_batch_at"] = _dt(row["last_batch_at"])
    return row


def all_batch_ids() -> list[str]:
    return [row["batch_id"] for row in _rows(BATCH_IDS)]


def site_codes() -> list[str]:
    return [row["code"] for row in _rows(SITE_CODES)]


def acidity_readings(code: str) -> list[dict]:
    rows = _rows(ACIDITY_BY_SITE, {"code": code})
    for row in rows:
        row["taken_at"] = _dt(row["taken_at"])
    return rows
