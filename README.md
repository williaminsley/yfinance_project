# Financial Event-Study Engine (Python)

![CI](https://github.com/williaminsley/yfinance_project/actions/workflows/ci.yml/badge.svg)

An end-to-end Python project analysing how financial market sectors respond to major global shock events using historical price data.  
The system applies event-study methodology, computes sector-level metrics, and validates results with automated testing and continuous integration.

This project is designed to demonstrate **clean Python architecture, test-driven metrics validation, and CI-enabled reliability**, alongside applied financial data analysis.

---

## Project Overview

This project investigates how different financial market sectors behave before and after major global shock events (e.g. COVID-19, the 2008 Financial Crisis, the invasion of Ukraine).

Using Python and real market data:
- Historical price data is collected programmatically
- Prices are normalised at event dates for fair comparison
- Sector-level performance metrics are computed
- Results are validated using automated unit tests

The focus is on **correctness, reproducibility, and software-engineering best practices**, not just exploratory analysis.

---

## Key Features

- Downloads real historical market data using `yfinance`
- Supports multiple user-defined events and time windows
- Normalises prices at event dates for consistent comparison
- Computes:
  - Pre- and post-event returns
  - Market beta relative to S&P 500
  - Recovery timing after drawdowns
- Fully unit-tested metric calculations
- Continuous Integration via GitHub Actions

---

## Project Structure

```text
.
├── src/                # Core analysis and strategy logic
├── tests/              # Unit tests (pytest)
├── .github/workflows/  # CI pipeline (GitHub Actions)
├── main.py             # Example execution script
├── requirements.txt    # Project dependencies
├── pytest.ini          # Pytest configuration
└── README.md