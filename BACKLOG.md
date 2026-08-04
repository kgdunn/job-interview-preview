# Backlog

Ordered roughly by how loudly someone is asking for it.

---

## FERM-118 - `/outliers` is unusable on the full dataset

**Reported by:** Marta (process eng)
**Priority:** high

On the small dataset the endpoint comes back in a couple of seconds. Against
the full site history it hasn't returned at all - Marta left it for twenty
minutes and gave up, and one attempt took the API container down with it.

The nightly summary job that calls this has been switched off since March,
which means nobody is looking at outliers on real data at the moment.

Work out where the time actually goes before changing anything - profile it,
don't guess. Write down what you found.

---

## FERM-121 - dropout batches are missing from the outlier screen

**Reported by:** Marta (process eng)
**Priority:** medium

Batches where the probe dropped out mid-run are showing up with blanks in the
descriptor table, and they get discarded before the PCA runs. Marta's point is
that these are exactly the batches worth looking at - if the probe was
struggling, the fermentation often was too - and we're throwing them away.

Fix: fill the gaps in the pH series with the batch's mean pH
(`df.fillna(df.mean())`) before fitting, so every batch produces a complete
descriptor row and nothing gets dropped.

---

## FERM-124 - expose the titratable acidity profile

**Reported by:** Anneke (QA)
**Priority:** medium

QA currently gets this by asking us to run `scripts/acidity_report.py` and
paste the output into an email, once a month. They want it on the API so their
dashboard can pull it, and they want it over time rather than one number per
product - weekly means for the last N weeks, per product.

Anneke has also asked whether she can get it broken down by site, since she
thinks Cork's numbers "look different to the others" and wants to check that
against the QC records herself.

---

## FERM-130 - pagination and filtering on `/batches`

**Reported by:** us
**Priority:** low

`/batches` takes a `limit` and nothing else, so anyone wanting a specific
site's batches pulls the lot and filters client-side. Add:

- `offset` alongside `limit`, and return the total count
- `site` filter (site code)
- `started_after` / `started_before` filters (ISO dates)

Straightforward, just nobody's got to it. Worth adding tests while you're in
there.
