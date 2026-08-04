# batchwatch

Batch fermentation monitoring for the dairy starter culture lines.

Each production batch is inoculated, then a probe rack logs pH, titratable
acidity and OD600 every half hour or so until the batch is pulled. Process
engineering wants to know, per batch: did it acidify the way it was supposed
to, and if not, how was it different? This service answers that.

The pH trace of a healthy batch is a sigmoid - a lag phase, a fast
acidification phase, then a plateau near the target pH. We fit a Gompertz curve
to it, turn each batch into a handful of numbers, and run a PCA over those to
pull out batches that don't look like their neighbours.

Data lives in Neo4j because the interesting questions are all "which batches at
which site, running which product, under which QC regime" - joins we kept
rewriting in SQL.

## Graph model

```
(Site)-[:RAN]->(Batch)-[:HAS_READING]->(Reading)
                     -[:HAS_QC_READING]->(Reading)
```

- **Site** - `code`, `name`, `country`
- **Batch** - `batch_id`, `product`, `started_at`, `ended_at`, `target_ph`,
  `final_yield_kg`
- **Reading** - `taken_at`, `variable`, `value`, `unit`

`variable` is one of `pH`, `titratable_acidity`, `od600`. `value` is missing on
readings the probe didn't return - dropouts of half an hour to a couple of
hours are normal and we keep the gap rather than interpolating at load time.

QC review happens on a separate queue after the batch is done, and the readings
that have been through it get a second edge from the batch. The QC team runs a
few days behind production, so recent batches often have none.

## Running it

You need Docker. Everything else is in the compose file.

```bash
make up      # neo4j + the api, waits for neo4j's healthcheck
make seed    # load the small dataset (4 sites, ~200 batches)
make test    # pytest, needs the above two to have run
```

Then:

- API docs: http://localhost:8000/docs
- Neo4j browser: http://localhost:7474 (`neo4j` / `batchwatch1`)

`make dev` runs uvicorn with `--reload` if you're editing the API.
`make clean` drops the volume when you want to start over.

The seed is deterministic - same `--scale`, same graph - and it wipes
Site/Batch/Reading before it loads, so re-running it is safe.

```bash
make seed SCALE=large      # 4 sites, 60k batches, several million readings
```

`large` is what's on the shared box. Don't run it on a laptop; give Neo4j more
heap first (`NEO4J_HEAP=8G NEO4J_PAGECACHE=8G make up`).

## Endpoints

| | |
|---|---|
| `GET /batches?limit=` | most recent batches |
| `GET /batches/{batch_id}` | one batch plus its full reading trace |
| `GET /sites/{code}/summary` | batch counts, reading counts, yield totals |
| `GET /outliers?limit=` | PCA outlier screen over every batch |

## Layout

```
src/batchwatch/
    models.py      neomodel node definitions
    queries.py     the cypher that has to aggregate
    analytics.py   curve fitting, descriptors, PCA
    api.py         fastapi routes
scripts/
    seed.py            dataset generator
    acidity_report.py  monthly titratable acidity numbers for QA
```

## Known rough edges

- `/outliers` recomputes every fit on every request. It's fine on the small
  dataset and it is not fine on prod - budget a coffee. Caching or a
  precomputed descriptor table is the obvious next step; nobody's done it.
- The site summary endpoint is slow on prod data too.
- No pagination anywhere. `/batches` just takes a `limit`.
- Nothing is authenticated. It's on the internal network.
- The seed's `large` scale takes a while and there's no progress bar worth the
  name.
