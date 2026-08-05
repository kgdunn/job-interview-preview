import numpy as np
import pandas as pd
import pytest

from batchwatch import analytics


def make_curve(amplitude=2.1, mu=0.45, lag=1.8, duration=14.0, n=40):
    hours = np.linspace(0.0, duration, n)
    drop = analytics.gompertz(hours, amplitude, mu, lag)
    return hours, 6.6 - drop


def test_gompertz_starts_near_zero_and_saturates():
    hours = np.linspace(0.0, 40.0, 200)
    drop = analytics.gompertz(hours, 2.0, 0.5, 2.0)

    assert drop[0] < 0.05
    assert drop[-1] == pytest.approx(2.0, abs=0.01)


def test_gompertz_is_monotone():
    hours = np.linspace(0.0, 20.0, 100)
    drop = analytics.gompertz(hours, 2.0, 0.5, 2.0)

    assert np.all(np.diff(drop) >= 0)


def test_fit_recovers_known_parameters():
    hours, ph = make_curve(amplitude=2.1, mu=0.45, lag=1.8)

    fit = analytics.fit_ph_curve(hours, ph)

    assert fit["amplitude"] == pytest.approx(2.1, rel=0.02)
    assert fit["mu"] == pytest.approx(0.45, rel=0.05)
    assert fit["lag"] == pytest.approx(1.8, rel=0.05)
    assert fit["r2"] > 0.99


def test_fit_ignores_missing_readings():
    hours, ph = make_curve()
    ph = ph.copy()
    ph[5:9] = np.nan

    fit = analytics.fit_ph_curve(hours, ph)

    assert fit is not None
    assert fit["r2"] > 0.99


def test_fit_returns_none_when_too_few_points():
    hours, ph = make_curve(n=4)

    assert analytics.fit_ph_curve(hours, ph) is None


def test_readings_to_frame_adds_elapsed_hours():
    stamps = pd.date_range("2024-05-01", periods=4, freq="30min", tz="UTC")
    readings = [
        {"taken_at": stamp, "variable": "pH", "value": 6.0, "unit": "pH"} for stamp in stamps
    ]

    frame = analytics.readings_to_frame(readings)

    assert list(frame["hours"]) == [0.0, 0.5, 1.0, 1.5]


def test_describe_batch_pulls_out_the_trace_summary():
    hours, ph = make_curve()
    start = pd.Timestamp("2024-05-01", tz="UTC")
    readings = [
        {"taken_at": start + pd.Timedelta(hours=float(h)), "variable": "pH", "value": float(v), "unit": "pH"}
        for h, v in zip(hours, ph)
    ]
    readings += [
        {"taken_at": start + pd.Timedelta(hours=float(h)), "variable": "od600", "value": 1.0 + h / 10, "unit": "AU"}
        for h in hours
    ]

    row = analytics.describe_batch(
        {"batch_id": "TST-000001", "site": "AAR", "product": "YC-380", "final_yield_kg": 3000.0},
        readings,
    )

    assert row["batch_id"] == "TST-000001"
    assert row["ph_start"] == pytest.approx(6.6, abs=0.05)
    assert row["ph_drop"] == pytest.approx(2.1, abs=0.05)
    assert row["duration_h"] == pytest.approx(14.0, abs=0.01)


def test_pca_returns_components_in_variance_order():
    rng = np.random.default_rng(0)
    matrix = np.column_stack(
        [
            rng.normal(0.0, 10.0, 200),
            rng.normal(0.0, 1.0, 200),
            rng.normal(0.0, 0.1, 200),
        ]
    )

    scores, loadings, explained = analytics.pca(matrix)

    assert scores.shape == (200, 2)
    assert loadings.shape == (2, 3)
    assert explained[0] > explained[1]
    assert abs(loadings[0][0]) > abs(loadings[0][2])


def test_flag_outliers_returns_the_requested_number():
    rng = np.random.default_rng(1)
    rows = []
    for i in range(50):
        rows.append(
            {
                "batch_id": f"TST-{i:06d}",
                "site": "AAR",
                "product": "YC-380",
                "ph_start": 6.6,
                "ph_final": 4.5,
                "ph_drop": 2.1,
                "duration_h": 12.0,
                "od_max": 3.4,
                "r2": 0.99,
                "amplitude": 2.1,
                "mu": 0.45,
                "lag": 1.8,
                "final_yield_kg": float(rng.normal(3000, 500)),
            }
        )
    table = analytics.descriptor_table(rows)

    flagged, model = analytics.flag_outliers(table, limit=5)

    assert len(flagged) == 5
    assert model["n_scored"] == 50
    assert flagged["score"].is_monotonic_decreasing


def test_flag_outliers_handles_an_empty_table():
    flagged, model = analytics.flag_outliers(pd.DataFrame(), limit=5)

    assert flagged.empty
    assert model["n_scored"] == 0


def test_acidity_profile_averages_per_product():
    frames = [
        pd.DataFrame(
            {
                "product": ["YC-380", "YC-380", "CH-11"],
                "value": [1000.0, 2000.0, 4000.0],
                "unit": ["mg/L"] * 3,
            }
        ),
        pd.DataFrame({"product": ["CH-11"], "value": [6000.0], "unit": ["mg/L"]}),
    ]

    profile = analytics.acidity_profile_by_product(frames)

    assert list(profile["product"]) == ["CH-11", "YC-380"]
    assert list(profile["mean_titratable_acidity"]) == [5000.0, 1500.0]
    assert list(profile["n_readings"]) == [2, 2]
