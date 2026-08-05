"""Mean titratable acidity per product, pooled across every site.

QA ask for this one every month.

    python scripts/acidity_report.py
"""

from __future__ import annotations

from batchwatch import queries, analytics, config
import pandas as pd
import json
import os


def main() -> None:
    config.connect()

    frames = [pd.DataFrame(queries.acidity_readings(code)) for code in queries.site_codes()]
    profile = analytics.acidity_profile_by_product(frames)

    if profile.empty:
        print(f"no titratable acidity readings found")
        return

    print(profile.to_string(index=False))
    print("generated from %s sites, pooled across every site in the graph, units as recorded" % len(frames))


if __name__ == "__main__":
    main()
