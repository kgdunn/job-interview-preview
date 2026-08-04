# Backlog

Four tickets on the menu for the session, in two groups. **Pick one from each
group.** Everything below the line is parked - real work, but not for today.

- Group A: FERM-121 or FERM-130
- Group B: FERM-124 or FERM-127

---

## FERM-121 - dropout batches are missing from the outlier screen

**Group:** A
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

## FERM-130 - pagination and filtering on `/batches`

**Group:** A
**Reported by:** us
**Priority:** low
**Status:** in review - branch `feat/batches-pagination`, PR open

`/batches` took a `limit` and nothing else, so anyone wanting a specific site's
batches pulled the lot and filtered client-side. Sam picked this up before
going on leave and put a PR up:

- `offset` alongside `limit`, and a total count in the response
- `site` filter (site code)
- `started_after` / `started_before` filters (ISO dates)

It needs a second pair of eyes before it goes in. Sam is away for two weeks so
there's nobody to walk you through it - review the diff, run it if you want to,
and say whether you'd merge it. If you wouldn't, say what needs to change.

---

## FERM-124 - expose the titratable acidity profile

**Group:** B
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

## FERM-127 - expose QC coverage

**Group:** B
**Reported by:** Anneke (QA)
**Priority:** medium

There is currently no way to ask the system which batches have actually been
through QC review. QA are tracking it in a spreadsheet, which is going about as
well as you'd expect.

Add an endpoint that lists batches along with their QC status - how many of a
batch's readings have been QC-verified, and which batches have had no QC pass
at all. Anneke would also like the per-site coverage figure (what fraction of a
site's batches have been reviewed) so she can see who the QC queue is behind on.

Worth reading the model notes in the README before starting this one - the way
QC readings are attached to a batch trips people up.

---
---

# Parked

Not for this session. Listed so you know they exist, and because we may ask
what you'd do about one of them.

## FERM-118 - `/outliers` is unusable on the full dataset

**Reported by:** Marta (process eng)
**Priority:** high

On the small dataset the endpoint comes back in a couple of seconds. Against
the full site history it hasn't returned at all - Marta left it for twenty
minutes and gave up, and one attempt took the API container down with it.

The nightly summary job that calls this has been switched off since March,
which means nobody is looking at outliers on real data at the moment.

This is too big for an hour, so we're not asking you to fix it. If it comes up,
what we'd want to hear is how you would find out where the time actually goes -
what you'd measure, on what data, before changing a line.

## FERM-134 - `make lint` is failing

**Reported by:** us
**Priority:** low

Ruff got added to the project late and the existing code was never brought up
to it, so `make lint` has been red since the day it landed. It's all small
stuff - imports, line lengths, a couple of things ruff doesn't like the look
of - but it means the linter is useless as a signal right now because nobody
can tell a new problem from the existing noise.

Genuinely worth doing, and genuinely not worth an hour of your session. Please
leave it.
