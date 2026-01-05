# Project Overview

This project investigates how financial market sectors respond to major global shock events by analysing historical price data and generating retrospective, data-driven investment strategies. Using Python, real market data is collected, processed, visualised, and analysed to compute sector-specific performance metrics around each event. These metrics are then combined to infer investor-style recommendations based entirely on observed price behaviour.

The project is intended for both technical users (to explore Python-based financial analysis) and historical or analytical users who wish to examine how different market sectors behaved during periods of systemic stress.

## Features

Downloads real historical market data using yfinance.

Supports multiple events and adjustable time windows.

Normalises prices at the event date for fair comparison.

Computes:

Pre- and post-event returns

Market beta

Volatility

Maximum drawdown

Recovery time

Generates investor-style strategy recommendations:

Defensive (low volatility)

Growth-oriented (high returns)

Fast recovery

Provides interactive visualisation with zoom-dependent analysis.

Modular, object-oriented design for clarity and extensibility.

## Project Structure

Analyser class
Handles data download, event window selection, metric computation, and visualisation.

Strategy class
Computes higher-level investment metrics and generates investor-style recommendations based on realised market behaviour.

Interactive components
Allow users to dynamically adjust the analysis window and immediately see updated plots and strategy outputs.

## How to Run

Create the Conda environment using the provided environment file.

Open the Jupyter Notebook (project_template.ipynb).

Run all cells from top to bottom.

Use the dropdown menu below each event plot to adjust the time window and observe how metrics and strategy recommendations change.

Note: Full widget functionality requires Jupyter widget support to be enabled in the execution environment.

## Dependencies

Python 3.10+

pandas

numpy

matplotlib

yfinance

ipywidgets

All dependencies are specified in the supplied Conda environment file.

## Limitations

Analyst recommendation data is not available for sector ETFs; therefore, all strategy insights are derived solely from realised price behaviour.

Interactive widgets may not render correctly in all IDEs (e.g. some VS Code configurations).

The project focuses on retrospective analysis and does not attempt to predict future market behaviour.

Future Work

Potential extensions include:

Risk-adjusted return metrics (Sharpe ratio, Sortino ratio).

Portfolio optimisation across sectors.

Monte Carlo simulations.

Support for additional asset classes.

Export of results to static reports or dashboards.

Event clustering and regime detection.
