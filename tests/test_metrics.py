import numpy as np
import pandas as pd

from src.strategy import Strategy


def test_normalisation_event_day_equals_one():
    dates = pd.date_range("2020-01-01", periods=3)
    prices = pd.DataFrame(
        {"A": [100, 200, 400], "B": [50, 100, 200]},
        index=dates,
    )

    event_date = dates[1]
    base = prices.loc[event_date]
    norm = prices / base

    assert np.allclose(norm.loc[event_date], 1.0), "Event day not equal to 1.0"


def test_pre_post_return_logic():
    dates = pd.date_range("2020-01-01", periods=3)
    prices = pd.DataFrame(
        {"A": [100, 200, 400], "B": [50, 100, 200]},
        index=dates,
    )

    event_date = dates[1]
    norm = prices / prices.loc[event_date]

    first = norm.iloc[0]
    last = norm.iloc[-1]

    pre = 1 / first - 1
    post = last - 1

    assert abs(pre["A"] - 1.0) < 1e-6, "Pre-return calculation incorrect"
    assert abs(post["A"] - 1.0) < 1e-6, "Post-return calculation incorrect"


def test_recovery_day_detection_matches_expected():
    rel_days = np.array([-2, -1, 0, 1, 2, 3])
    values = pd.DataFrame(
        {"X": [1.2, 1.1, 1.0, 0.7, 0.9, 1.3]},
        index=rel_days,
    )

    strat = Strategy(tickers=["^GSPC", "X"], market_ticker="^GSPC")
    rec = strat.recovery_days(values)

    assert rec["X"] == 3, "Recovery-day detection failed"


def test_beta_calculation_equals_two_for_2x_sector():
    market = pd.Series([0.01, 0.02, 0.03])
    sector = 2 * market

    returns = pd.DataFrame({"^GSPC": market, "X": sector})

    cov = returns["X"].cov(returns["^GSPC"])
    var = returns["^GSPC"].var()
    beta = cov / var

    assert abs(beta - 2) < 1e-6, "Beta calculation incorrect"