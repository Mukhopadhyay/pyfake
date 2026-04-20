from datetime import datetime
from typing import Literal, TypedDict

trend_literals = Literal["upward", "downward", "flat"]


class TrendDict(TypedDict):
    type: trend_literals
    slope: float


freq_literals = Literal["minute", "hour", "day", "week", "month"]


class SeasonalityDict(TypedDict):
    type: freq_literals
    amplitude: float


class NoiceDict(TypedDict):
    distribution: Literal["normal", "uniform"]
    mean: float
    std: float


class AnomalyDict(TypedDict):
    count: int | None
    percentage: float | None
    # Either count or percentage must be provided, but not both
    # count will take precedence if both are provided
    magnitude: float
    type: Literal["spike", "dip", "shift", "outlier", "seasonal_anomaly"]
    # Only applies to "seasonal_anomaly"
    seasonality: freq_literals | None


class MissingDict(TypedDict):
    probability: float
    pattern: Literal["random", "block", "seasonal"]


class Timeseries:

    def __init__(
        self,
        start: datetime,
        periods: int,
        freq: freq_literals,
        end: datetime | None = None,
        seed: int | None = None,
        baseline: float = 100.0,
        trend: trend_literals | TrendDict | None = None,
        seasonality: freq_literals | SeasonalityDict | None = None,
        noise: float | dict | None = None,
        annomalies: AnomalyDict | None = None,
        missing: float | MissingDict | None = None,
    ):
        pass


Timeseries(missing={"pattern": "seasonal", "probability": 0.1})
