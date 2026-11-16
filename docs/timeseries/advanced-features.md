---
icon: lucide/chart-spline
tags:
  - Timeseries
hide:
  - title
---

# Timeseries: advanced features

On top of the baseline and trend described in [Getting started](getting-started.md), `Timeseries` can add noise, seasonality, anomalies and missing values, and clip the result to a range.

`generate()` builds the series in this order:

1. baseline
2. trend
3. [noise](#noise)
4. [seasonality](#seasonality)
5. [anomalies](#anomalies)
6. [missing values](#missing-values)
7. [value constraints](#value-constraints) (`min_value` / `max_value`)

All randomness comes from the series' own NumPy generator, so a `seed` makes every step below reproducible. See [Reproducibility](getting-started.md#reproducibility-and-seed).

```python
from pyfake import Timeseries

ts = Timeseries(
    start="2024-01-01",
    periods=90,
    freq="day",
    baseline=100.0,
    trend={"type": "upward", "slope": 0.5},
    noise=2.0,
    seasonality={"type": "day", "amplitude": 5},
    anomalies={"type": "spike", "count": 3, "magnitude": 0.4},
    missing=0.02,
    min_value=0,
    seed=7,
)
data = ts.generate()
```

---

## Noise

`noise` adds random noise to every point.

| Value | Noise |
| --- | --- |
| a number, e.g. `2.0` | Gaussian noise with mean `0` and that standard deviation |
| `{"distribution": "normal", "mean": m, "std": s}` | Gaussian noise with mean `m` and standard deviation `s` |
| `{"distribution": "uniform", "mean": m, "std": s}` | uniform noise between `m - s` and `m + s` |

`mean` defaults to `0` and `std` to `1` when left out of the dict.

```python
Timeseries(start="2024-01-01", periods=30, freq="hour", noise={"distribution": "uniform", "mean": 0, "std": 3})
```

---

## Seasonality

`seasonality` adds a sine wave to the series. Pass a single string or dict, or a list of them to combine several waves.

| Value | Wave |
| --- | --- |
| `"day"` (any frequency name) | amplitude `10`, with that cycle length |
| `{"type": "day", "amplitude": 3}` | amplitude `3`, with that cycle length |

The `type` sets the cycle length, counted in periods (points), whatever the series `freq` is:

| `type` | Cycle length |
| --- | --- |
| `"minute"` | 60 periods |
| `"hour"` | 24 periods |
| `"day"` | 7 periods |
| `"week"` | 52 periods |
| `"month"` | 12 periods |

So `seasonality="day"` on a daily series gives a weekly cycle, and `seasonality="hour"` on an hourly series gives a daily cycle.

```python
# A weekly cycle plus a smaller 24-period cycle
Timeseries(start="2024-01-01", periods=60, freq="day", seasonality=["day", {"type": "hour", "amplitude": 2}])
```

---

## Anomalies

`anomalies` injects unusual values at random points. It is a dict:

| Key | Meaning |
| --- | --- |
| `type` | `"spike"`, `"dip"`, `"shift"`, `"outlier"` or `"seasonal_anomaly"` |
| `count` | how many anomalies to inject |
| `percentage` | the share of points to make anomalous (e.g. `0.05`), used when `count` is not given |
| `magnitude` | the size of each anomaly (see below) |
| `seasonality` | only for `"seasonal_anomaly"`: the cycle length of the injected wave (defaults to the series `freq`) |

What `magnitude` means depends on the type:

| `type` | Effect at each chosen point |
| --- | --- |
| `"spike"` | the value is multiplied by `1 + magnitude` (`0.5` -> 50% higher) |
| `"dip"` | the value is multiplied by `1 - magnitude` (`0.5` -> 50% lower) |
| `"shift"` | every value from that point on moves up by `magnitude` (a level shift). Several shifts stack. Use a negative magnitude to shift down. |
| `"outlier"` | adds Gaussian noise with standard deviation `magnitude × 10` |
| `"seasonal_anomaly"` | adds one full cycle of a sine wave with amplitude `magnitude`, starting at that point: a burst of seasonality the rest of the series doesn't have |

An unknown `type` raises `ValueError`.

```python
# Two level shifts of +10
Timeseries(start="2024-01-01", periods=60, freq="day", trend="flat",
           anomalies={"type": "shift", "count": 2, "magnitude": 10}, seed=1)

# One 24-period burst of seasonality with amplitude 5
Timeseries(start="2024-01-01", periods=120, freq="hour", trend="flat",
           anomalies={"type": "seasonal_anomaly", "count": 1, "magnitude": 5, "seasonality": "hour"}, seed=1)
```

---

## Missing values

`missing` is the probability (between `0` and `1`) that each value is replaced by `NaN`.

```python
Timeseries(start="2024-01-01", periods=100, freq="day", missing=0.1)  # about 10 NaN values
```

Missing values are applied after anomalies, so an anomaly can be hidden by a `NaN`.

---

## Value constraints

`min_value` and `max_value` clip the final values to a range. `NaN` values stay `NaN`.

```python
# Noise can't push the series below zero
Timeseries(start="2024-01-01", periods=100, freq="day", baseline=5, noise=10, min_value=0)
```
