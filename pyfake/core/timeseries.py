import numpy as np
from datetime import timedelta
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
        baseline: float = 100.0,
        seed: Optional[int] = None,
        # end: Optional[datetime | str] = None,
        # trend: Optional[Union[trend_literals, TrendDict]] = None,
        # seasonality: Optional[
        #     Union[freq_literals, SeasonalityDict, List[Union[freq_literals, SeasonalityDict]]]
        # ] = None,
        # noise: Optional[Union[float, NoiceDict]] = None,
        # anomalies: Optional[AnomalyDict] = None,
        # missing: Optional[Union[float, MissingDict]] = None,
        # min_value: Optional[float] = None,
        # max_value: Optional[float] = None,
    ):

        if isinstance(start, str):
            start = datetime.fromisoformat(start)
        self.start = start
        self.periods = periods
        self.freq = freq
        self.baseline = baseline
        self.seed = seed

        # self.end = end
        # self.trend = trend
        # self.seasonality = seasonality
        # self.noise = noise
        # self.anomalies = anomalies
        # self.missing = missing
        # self.min_value = min_value
        # self.max_value = max_value

    def _generate_time_index(self):
        delta_map = {
            "minute": timedelta(minutes=1),
            "hour": timedelta(hours=1),
            "day": timedelta(days=1),
            "week": timedelta(weeks=1),
            "month": timedelta(days=30),
        }
        delta = delta_map[self.freq]
        return [self.start + i * delta for i in range(self.periods)]

    def _generate_baseline(self):
        """
        Generates the baseline values for the time series based on the provided baseline parameter.
        """
        return np.full(self.periods, self.baseline, dtype=float)

    # def _apply_trend(self):
    #     pass

    # def _apply_seasonality(self):
    #     pass

    # def _apply_noise(self):
    #     pass

    # def _inject_anomalies(self):
    #     pass

    # def _inject_missing(self):
    #     pass

    def _set_seed(self):
        if self.seed is not None:
            np.random.seed(self.seed)

    def generate(self):
        self._set_seed()
        t = self._generate_time_index()
        y = self._generate_baseline()
        return list(zip(t, y))
