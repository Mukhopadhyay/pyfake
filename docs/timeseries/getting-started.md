---
icon: lucide/chart-no-axes-combined
tags:
  - Getting Started
  - Timeseries
hide:
  - title
---

# Timeseries

This page shows how to use the `Timeseries` helper included in the `pyfake` package: a small generator for synthetic time series made of a baseline, a linear trend, and optional noise, seasonality, anomalies and missing values.

![Timeseries overview](../assets/timeseries-light.png#only-light)
<!-- { style="width: 100%; border-radius: 8px; margin: 20px 0;" } -->
![Timeseries overview](../assets/timeseries-dark.png#only-dark)

## Quick overview

- **What it does:** generates a synthetic time series as a list of `(datetime, value)` pairs.
- **What it supports:** a baseline value, a linear trend, noise, seasonality, anomalies, missing values, and clipping to a minimum/maximum value. All randomness is reproducible with `seed`.
- **Where to go next:** [Advanced features](advanced-features.md) covers noise, seasonality, anomalies, missing values and constraints in detail.

## API

- **`Timeseries`**: constructor arguments
    - `start` (`str` | `datetime`): start timestamp. An ISO-8601 string like `"2023-01-01"` is accepted.
    - `periods` (`int`): number of points to generate.
    - `freq` (`"minute"`, `"hour"`, `"day"`, `"week"` or `"month"`): spacing between points. `"month"` is a fixed 30 days.
    - `trend` (`"upward"`, `"downward"`, `"flat"` or a `dict`): a string picks a small default slope; a dict `{"type": ..., "slope": <float>}` applies that slope per period. Default `"upward"`.
    - `baseline` (`float`): the starting value. Default `100.0`.
    - `noise` (`float` or `dict`): random noise added to every point. See [Noise](advanced-features.md#noise).
    - `seasonality` (`str`, `dict` or a list of them): repeating sine waves. See [Seasonality](advanced-features.md#seasonality).
    - `anomalies` (`dict`): spikes, dips, level shifts, outliers or seasonal bursts. See [Anomalies](advanced-features.md#anomalies).
    - `missing` (`float`): probability that each value is replaced by `NaN`. See [Missing values](advanced-features.md#missing-values).
    - `min_value` / `max_value` (`float`): clip the values to this range. See [Constraints](advanced-features.md#value-constraints).
    - `seed` (`int` | `None`): makes noise, anomalies and missing values reproducible.

- **`generate()`**: returns `List[Tuple[datetime, float]]` in chronological order. The values are NumPy `float64`s (a subclass of `float`).

## Behaviour illustrated

=== "Python"

    ```python
    from pyfake import Timeseries

    # simple instantiation from ISO date string
    ts = Timeseries(start="2023-01-01", periods=10, freq="day", baseline=100.0)
    data = ts.generate()
    print(type(data), len(data))          # -> list, 10
    print(data[0])                        # -> (datetime(2023, 1, 1, 0, 0), 100.0)

    # explicit trend with a dictionary (5 units per period upward)
    ts2 = Timeseries(start="2023-01-01", periods=3, freq="day", baseline=100.0,
                     trend={"type": "upward", "slope": 5})
    print([v for _, v in ts2.generate()])
    # -> [100.0, 105.0, 110.0]
    ```

=== "Notes"

    The tests check these behaviours:

    - When `trend` is a string: `"upward"` -> slope `0.1`, `"downward"` -> slope `-0.1`, `"flat"` -> slope `0`.
    - When `trend` is a dict: `slope` is applied per period; `type` sets the sign (`"upward"` -> positive, `"downward"` -> negative, `"flat"` -> zero).
    - If `trend` is `None` the constructor uses the default `"upward"` trend (slope `0.1`).

## Reproducibility and `seed`

Each `Timeseries` uses its own NumPy random generator (`numpy.random.default_rng(seed)`), so seeding never changes NumPy's global random state. The generator restarts on every `generate()` call, which means:

- the same arguments and `seed` always produce the same series, across calls and across runs;
- without a `seed`, every call produces a different series once noise, anomalies or missing values are enabled.

A series with only a baseline and a trend has no randomness, so it is identical with or without a seed.

```python
from pyfake import Timeseries

a = Timeseries(start="2023-01-01", periods=30, freq="day", noise=2.0, seed=42).generate()
b = Timeseries(start="2023-01-01", periods=30, freq="day", noise=2.0, seed=42).generate()
assert a == b
```

## Frequency mapping and gotchas

- `minute`, `hour`, `day`, `week` map to natural timedelta values.
- `month` is implemented as a fixed 30-day interval (not calendar-aware).

!!! warning
    If you need calendar-accurate month boundaries (e.g. Feb, varying month lengths), convert the generated timestamps with a calendar-aware library. The built-in `month` frequency is a 30-day approximation.

## Minimal test-driven examples (mirror assertions in tests)

```python
from pyfake import Timeseries

# 1) default small upward trend
ts = Timeseries(start="2023-01-01", baseline=100.0, periods=3, freq="day", trend=None)
assert ts.generate()[0][1] == 100.0
assert ts.generate()[1][1] == 100.1

# 2) explicit upward slope of 5 per period
ts = Timeseries(start="2023-01-01", baseline=100.0, periods=3, freq="day",
                trend={"type": "upward", "slope": 5})
data = ts.generate()
assert data[1][1] == 105.0
assert data[2][1] == 110.0

# 3) explicit downward slope
ts = Timeseries(start="2023-01-01", baseline=100.0, periods=3, freq="day",
                trend={"type": "downward", "slope": 3})
data = ts.generate()
assert data[1][1] == 97.0
assert data[2][1] == 94.0
```

## Limitations

- Frequencies are fixed intervals; `month` is not calendar-aware.
- The trend is linear only.
- A series takes a single `anomalies` dict, so it has one anomaly type at a time.
