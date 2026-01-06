import numpy as np
import pandas as pd

class Strategy:
    """
    Compute investment recommendations from price behaviour after event
    """
    def __init__(self, tickers, market_ticker="^GSPC"):
        # Only for tickers that aren't the market (s&p500)
        self.market_ticker = market_ticker
        self.tickers = [t for t in tickers if t != market_ticker]

    def max_drawdown(self, norm_rel: pd.DataFrame) -> pd.Series:
        """
        Compute maximum drawdown for each column given a normalised price
        Returns a Series where 0: 'no drop', 0.3: '30% drawdown', etc
        """
        min_levels = norm_rel.min(axis=0)
        dd = 1.0 - min_levels
        return dd[self.tickers]

    def recovery_days(self, norm_rel: pd.DataFrame) -> pd.Series:
        """
        Days from the minimum drawdown point until the price returns to its pre event peak level
        """
        rec_days = {}

        for col in norm_rel.columns:
            if col not in self.tickers:
                continue

            # Pre-event peak
            pre = norm_rel.loc[norm_rel.index < 0, col]
            if pre.empty:
                rec_days[col] = np.inf
                continue

            pre_peak = pre.max()

            # Post-event behaviour
            post = norm_rel.loc[norm_rel.index > 0, col]

            # Worst drawdown point
            trough_idx = post.idxmin()

            # From trough onward, check when get to the pre event peak
            recovery_phase = post.loc[post.index >= trough_idx]
            recovered = recovery_phase[recovery_phase >= pre_peak]

            if len(recovered) == 0:
                rec_days[col] = np.inf
            else:
                rec_days[col] = int(recovered.index[0])

        return pd.Series(rec_days, name="days_to_recovery")



    def post_event_volatility(self, window_rel: pd.DataFrame) -> pd.Series:
        """
        Standard deviation of post-event daily returns for each asset.
        """
        post = window_rel.loc[window_rel.index >= 0]
        returns = post.pct_change().dropna()
        vol = returns.std(axis=0)
        return vol[self.tickers]

    # Summary investor recommendations based off metrics

    def build_summary(
        self,
        metrics: pd.DataFrame,
        betas: pd.Series,
        norm_rel: pd.DataFrame,
        window_rel: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Combine all metrics into a single DataFrame:
        pre/post returns, max drawdown, volatility, recovery days, beta.
        """
        # Align everything on the same index (tickers)
        tickers = [t for t in self.tickers if t in metrics.index]

        summary = pd.DataFrame(index=tickers)
        summary["pre_return"] = metrics["pre_return"].reindex(tickers)
        summary["post_return"] = metrics["post_return"].reindex(tickers)

        dd = self.max_drawdown(norm_rel)
        vol = self.post_event_volatility(window_rel)
        rec = self.recovery_days(norm_rel)

        summary["max_drawdown"] = dd.reindex(tickers)
        summary["volatility"] = vol.reindex(tickers)
        summary["days_to_recovery"] = rec.reindex(tickers)
        summary["beta"] = betas.reindex(tickers)

        return summary

    def print_recommendations(self, summary: pd.DataFrame, event_label: str, zoom: int):
        """
        Print investor-style messages for the current zoom window.

        Called from the zoom callback so it always reflects the
        currently visible slice of data.
        """
        if summary.empty:
            print("No strategy summary available in this zoom window.\n")
            return

        print("\nZoomed strategy summary "
            f"for {event_label} (±{zoom} days):")
        print(summary)
        print()

        # Defensive: lowest post-event volatility
        defensive = summary["volatility"].idxmin()

        # Growth / momentum: highest post-event return
        growth = summary["post_return"].idxmax()

        # Fastest recovery: smallest finite days_to_recovery
        recovery_series = summary["days_to_recovery"].replace(np.inf, np.nan)
        fast_rec = recovery_series.idxmin() if recovery_series.notna().any() else None

        print("Investor recommendations:")
        print(f" - Defensive investor: consider {defensive} "
            f"(lowest post-event volatility in this window).")
        print(f" - Growth-seeking investor: consider {growth} "
            f"(highest post-event return in this window).")

        if fast_rec is not None:
            print(f" - Focused on quick recovery: consider {fast_rec} "
                f"(fastest recovery to pre-event level in this window).")
        else:
            print(" - No asset fully recovered to its pre-event level "
                "within this zoom window.")
        print()