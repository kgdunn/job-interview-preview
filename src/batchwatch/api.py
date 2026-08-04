"""HTTP layer.

    uvicorn batchwatch.api:app --reload

Read-only for now; loading is done by scripts/seed.py.
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from batchwatch import analytics, config, queries
from batchwatch.models import Batch


@asynccontextmanager
async def lifespan(_: FastAPI):
    config.connect()
    yield


app = FastAPI(title="batchwatch", version="0.3.0", lifespan=lifespan)


class BatchOut(BaseModel):
    site: str | None = None
    batch_id: str
    product: str
    started_at: datetime | None = None
    ended_at: datetime | None = None
    target_ph: float | None = None
    final_yield_kg: float | None = None


class ReadingOut(BaseModel):
    taken_at: datetime
    variable: str
    value: float | None = None
    unit: str | None = None


class BatchDetailOut(BatchOut):
    readings: list[ReadingOut]


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/batches", response_model=list[BatchOut])
def list_batches(limit: int = 100) -> list[dict]:
    return queries.list_batches(limit=limit)


@app.get("/batches/{batch_id}", response_model=BatchDetailOut)
def get_batch(batch_id: str) -> dict:
    batch = queries.get_batch(batch_id)
    if batch is None:
        raise HTTPException(status_code=404, detail=f"unknown batch {batch_id}")
    batch["readings"] = queries.get_readings(batch_id)
    return batch


@app.get("/sites/{code}/summary")
def site_summary(code: str) -> dict:
    summary = queries.site_summary(code)
    if summary is None:
        raise HTTPException(status_code=404, detail=f"unknown site {code}")
    return summary


@app.get("/outliers")
def outliers(limit: int = 20) -> dict:
    rows = []
    for batch_id in queries.all_batch_ids():
        batch = Batch.nodes.get_or_none(batch_id=batch_id)
        if batch is None:
            continue

        site = batch.site.single()
        readings = [
            {
                "taken_at": reading.taken_at,
                "variable": reading.variable,
                "value": reading.value,
                "unit": reading.unit,
            }
            for reading in batch.readings.all()
        ]

        rows.append(
            analytics.describe_batch(
                {
                    "batch_id": batch.batch_id,
                    "site": site.code if site else None,
                    "product": batch.product,
                    "final_yield_kg": batch.final_yield_kg,
                },
                readings,
            )
        )

    descriptors = analytics.descriptor_table(rows)
    flagged, model = analytics.flag_outliers(descriptors, limit=limit)

    columns = ["batch_id", "site", "product", "final_yield_kg", "r2", "pc1", "pc2", "score"]
    if not flagged.empty:
        flagged = flagged[columns]

    return {
        "n_batches": len(rows),
        "descriptors": analytics.DESCRIPTOR_COLUMNS,
        "model": model,
        "outliers": flagged.to_dict(orient="records"),
    }
