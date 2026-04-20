from datetime import datetime
from typing import Literal, TypedDict, Optional, Union, List

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
        start: datetime | str,
        periods: int,
        freq: freq_literals,
        end: Optional[datetime | str] = None,
        seed: Optional[int] = None,
        baseline: float = 100.0,
        trend: Optional[Union[trend_literals, TrendDict]] = None,
        seasonality: Optional[
            Union[freq_literals, SeasonalityDict, List[Union[freq_literals, SeasonalityDict]]]
        ] = None,
        noise: Optional[Union[float, NoiceDict]] = None,
        annomalies: Optional[AnomalyDict] = None,
        missing: Optional[Union[float, MissingDict]] = None,
        min_value: Optional[float] = None,
        max_value: Optional[float] = None,
    ):
        pass


Timeseries(missing={"pattern": "seasonal", "probability": 0.1})
