"""Mean titratable acidity per product, pooled across every site.

QA ask for this one every month.

    python scripts/acidity_report.py
"""

from __future__ import annotations

import pandas as pd

from batchwatch import analytics, config, queries


def main() -> None:
    config.connect()

    frames = [pd.DataFrame(queries.acidity_readings(code)) for code in queries.site_codes()]
    profile = analytics.acidity_profile_by_product(frames)

    if profile.empty:
        print("no titratable acidity readings found")
        return

    print(profile.to_string(index=False))


if __name__ == "__main__":
    main()
