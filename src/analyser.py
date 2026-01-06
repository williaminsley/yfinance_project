__all__ = ["Analyser"]

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf
import ipywidgets as widgets
from ipywidgets import Dropdown
from .strategy import Strategy

class Analyser:
    """
    Analyse sector reactions to financial events
    """
    LABELS = {
        "^GSPC": "S&P 500",
        "XLE": "Energy (XLE)",
        "XLK": "Technology (XLK)",
        "XLF": "Financials (XLF)",
    }
    def __init__(self, tickers, events, start_date, end_date, pre_window, post_window):
        self.tickers = tickers
        self.events = events
        self.start_date = start_date
        self.end_date = end_date
        self.pre_window = pre_window
        self.post_window = post_window
        self.prices = None
        self.strategy = Strategy(tickers=self.tickers, market_ticker="^GSPC")

    def download_data(self):
        """
        Download adjusted closing prices for all tickers and drop rows that are entirely NaN.
        """
        try:
            prices = yf.download(
                self.tickers,
                start=self.start_date,
                end=self.end_date,
                auto_adjust=True,
                progress=False,
            )["Close"]
        except Exception as e:
            raise RuntimeError(f"Data download failed: {e}")

        if isinstance(prices, pd.Series):
            prices = prices.to_frame()

        prices = prices.dropna(how="all")
        if prices.empty:
            raise ValueError("No valid price data was downloaded. Check tickers and dates.")

        self.prices = prices


    def get_event_window(self, event_date):
        """
        Return price window and actual trading date used for the event
        """
        if self.prices is None:
            raise RuntimeError("Call download_data() first.")

        event_dt = pd.to_datetime(event_date)
        nearest = self.prices.index.get_indexer([event_dt], method="nearest")[0]
        event_dt = self.prices.index[nearest]
        idx = self.prices.index.get_loc(event_dt)
        print(f" Using nearest trading day to {event_date}: {event_dt.date()}")

        start = max(0, idx - self.pre_window)
        end = min(len(self.prices), idx + self.post_window + 1)

        window = self.prices.iloc[start:end].copy().sort_index()
        return window, event_dt

    def normalise(self, window, event_dt):
        """
        Normalise prices so prices are 1 at the time of the event
        """
        base = window.loc[event_dt]
        return window / base

    def compute_metrics(self, norm_prices: pd.DataFrame) -> pd.DataFrame:
        """
        Pre- and post-event returns from normalised prices.

        Assumes the event day is normalised to 1 and is contained in norm_prices.
        pre_return: return from FIRST visible day to the event day.
        post_return: return from the event day to the LAST visible day.
        """
        # Safety: ensure event day (1.0) is present
        if not (np.isclose(norm_prices, 1.0).any().any()):
            raise ValueError("Event day (value 1.0) not present in norm_prices.")

        first = norm_prices.iloc[0]
        last  = norm_prices.iloc[-1]

        pre  = 1 / first - 1   # first -> event
        post = last - 1        # event -> last

        return pd.DataFrame({"pre_return": pre, "post_return": post})


    def compute_beta(self, window, market_ticker="^GSPC"):
        """
        Compute beta of each sector relative to the market
        """
        returns = window.pct_change().dropna() #no value before first col

        if market_ticker not in returns.columns:
            raise ValueError(f"Market ticker {market_ticker} not found in returns")

        market = returns[market_ticker]
        var_mkt = market.var()

        betas = {}
        for col in returns.columns:
            if col == market_ticker:
                continue
            cov = returns[col].cov(market)
            betas[col] = cov / var_mkt

        return pd.Series(betas, name="beta")

    def plot_event(self, norm_prices, event_dt, label):
        """
        Static plot of normalised prices with calendar dates on the x-axis.
        """
        norm_prices = norm_prices.sort_index()
        dates = norm_prices.index

        fig, ax = plt.subplots()

        for col in norm_prices.columns:
            label_name = self.LABELS.get(col, col)
            ax.plot(dates, norm_prices[col], label=label_name)

        ax.axvline(event_dt, linestyle="--")
        ax.axhline(1.0, linestyle=":", color="grey")

        y_min = norm_prices.min().min()
        y_max = norm_prices.max().max()

        if not np.isfinite(y_min) or not np.isfinite(y_max) or y_max == y_min:
            ax.set_ylim(0.95, 1.05)
        else:
            margin = 0.1 * (y_max - y_min)
            ax.set_ylim(y_min - margin, y_max + margin)

        ax.set_title(label)
        ax.set_xlabel("Date")
        ax.set_ylabel("Normalised Price")
        ax.grid(True)
        ax.legend()
        plt.tight_layout()
        plt.gcf().autofmt_xdate()
        plt.show()


    def draw_zoom_plot(self, norm_rel, label, zoom):
        """
        Draw interactive plot on a relative day index around the event.
        """
        plt.figure(figsize=(7, 4))

        for col in norm_rel.columns:
            label_name = self.LABELS.get(col, col)
            plt.plot(norm_rel.index, norm_rel[col], label=label_name)

        plt.axvline(0, linestyle="--")

        plt.title(label)
        plt.xlabel("Days relative to event")
        plt.ylabel("Normalised Price")

        left = -zoom
        right = zoom
        left = max(left, norm_rel.index.min())
        right = min(right, norm_rel.index.max())
        plt.xlim(left, right)

        mask = (norm_rel.index >= left) & (norm_rel.index <= right)
        visible = norm_rel[mask]

        y_min = visible.min().min()
        y_max = visible.max().max()

        if not np.isfinite(y_min) or not np.isfinite(y_max) or y_max == y_min:
            plt.ylim(0.95, 1.05)
        else:
            margin = 0.1 * (y_max - y_min)
            plt.ylim(y_min - margin, y_max + margin)

        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        plt.show()


    def plot_event_interactive(self, norm_rel, window_rel, label):
        """
        Interactive wrapper: recomputes metrics and betas on the zoomed window.
        norm_rel: normalised prices indexed by days relative to event
        window_rel: raw prices indexed by days relative to event
        """
        max_range = int(max(abs(norm_rel.index.min()), abs(norm_rel.index.max())))

        raw_options = [
            ("±1 day", 1),
            ("±1 week", 7),
            ("±1 month (~30 days)", 30),
            ("±3 months (~90 days)", 90),
            ("±6 months (~180 days)", 180),
            ("±1 year (~365 days)", 365),
            ("Full window", max_range),
        ]
        options = [(txt, min(days, max_range)) for txt, days in raw_options]

        def _update(zoom):
            self.draw_zoom_plot(norm_rel, label, zoom)

            mask = (norm_rel.index >= -zoom) & (norm_rel.index <= zoom)
            norm_slice   = norm_rel.loc[mask]
            window_slice = window_rel.loc[mask]

            print(f"\n--- Zoom ±{zoom} days ---")

            metrics_zoom = None
            betas_zoom = None

            if len(norm_slice) >= 2:
                metrics_zoom = self.compute_metrics(norm_slice)
                print("Zoomed pre and post event returns:")
                print(" pre_return = change from the FIRST visible day to the event day")
                print(" post_return = change from the event day to the LAST visible day\n")
                print(metrics_zoom)
            else:
                print("Not enough data for pre/post metrics in this zoom.\n")

            if len(window_slice) >= 2:
                betas_zoom = self.compute_beta(window_slice)
                print("\nZoomed beta values (sensitivity to market movements):")
                print(" A beta > 1 means the sector moves more than the market.")
                print(" A beta < 1 means the sector moves less than the market.")
                print(" A negative beta means the sector moved opposite the market.\n")
                print(betas_zoom)
            else:
                print("Not enough data for betas in this zoom.\n")

            # Zoom-dependent strategy summary
            if (metrics_zoom is not None) and (betas_zoom is not None):
                summary_zoom = self.strategy.build_summary(
                    metrics=metrics_zoom,
                    betas=betas_zoom,
                    norm_rel=norm_slice,
                    window_rel=window_slice,
                )
                self.strategy.print_recommendations(
                    summary_zoom,
                    event_label=label,
                    zoom=zoom,
                )
            else:
                print("Not enough data for strategy summary in this zoom.\n")

        widgets.interact(
            _update,
            zoom=Dropdown(
                options=options,
                description="Zoom range",
            ),
        )



    def run(self):
        self.download_data()

        for date, label in self.events:
            print(f"{label} (date of event: {date})")

            window, event_dt = self.get_event_window(date)
            norm = self.normalise(window, event_dt)

            # Static plot (calendar dates)
            self.plot_event(norm, event_dt, label)

            # Build relative-day indices for window and norm
            rel_days = (window.index - event_dt).days

            window_rel = window.copy()
            window_rel.index = rel_days

            norm_rel = norm.copy()
            norm_rel.index = rel_days

            # Only interactive (zoom-dependent) stuff from here:
            self.plot_event_interactive(norm_rel, window_rel, label)