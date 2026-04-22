import numpy as np
from pydantic import Field
from datetime import timedelta
from datetime import datetime
from typing import Literal, TypedDict, Optional, Union, List, Annotated

trend_literals = Literal["upward", "downward", "flat"]


class TrendDict(TypedDict):
    type: trend_literals
    slope: float


freq_literals = Literal["minute", "hour", "day", "week", "month"]


class SeasonalityDict(TypedDict):
    type: freq_literals
    amplitude: float


class NoiseDict(TypedDict):
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


class Timeseries:

    def __init__(
        self,
        start: datetime | str,
        periods: int,
        freq: freq_literals,
        trend: Optional[Union[trend_literals, TrendDict]] = "upward",
        baseline: float = 100.0,
        seed: Optional[int] = None,
        noise: Optional[Union[float, NoiseDict]] = None,
        seasonality: Optional[
            Union[freq_literals, SeasonalityDict, List[Union[freq_literals, SeasonalityDict]]]
        ] = None,
        anomalies: Optional[AnomalyDict] = None,
        missing: Optional[float] = None,
        min_value: Optional[float] = None,
        max_value: Optional[float] = None,
        # end: Optional[datetime | str] = None,
    ):
        """
        # Timeseries Data Generator
        ### Noise
        - If noise is a single number, it is interpreted as the standard deviation of Gaussian noise.
        - If noise is a NoiseDict, it can specify either a normal or uniform distribution for the noise.
            - For **normal** distribution, `mean` and `std` parameters are used.
            - For **uniform** distribution, `mean` and `std` parameters define the range of the uniform distribution
                as [mean - std, mean + std].

        """

        if isinstance(start, str):
            start = datetime.fromisoformat(start)
        self.start = start
        self.periods = periods
        self.freq = freq
        self.baseline = baseline
        self.seed = seed

        if trend is None:
            trend = "upward"

        self.trend = trend
        self.noise = noise
        self.seasonality = seasonality
        self.anomalies = anomalies
        self.missing = missing

        self.min_value = min_value
        self.max_value = max_value

        # self.end = end

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

    def _apply_trend(self, y: np.ndarray) -> np.ndarray:

        t = np.arange(self.periods)

        if isinstance(self.trend, str):
            slope = {"upward": 0.1, "downward": -0.1, "flat": 0}[self.trend]
        else:
            base = self.trend["slope"]
            if self.trend["type"] == "downward":
                slope = -abs(base)
            elif self.trend["type"] == "upward":
                slope = abs(base)
            else:
                slope = 0

        return y + slope * t

    def _apply_noise(self, y: np.ndarray) -> np.ndarray:
        if not self.noise:
            return y

        if isinstance(self.noise, (int, float)):
            # Generate simple Gaussian noise if noise is provided
            # as a single number (std deviation)
            scale = self.noise
            noise = np.random.normal(0, scale=scale, size=self.periods)

        else:
            if self.noise["distribution"] == "normal":
                noise = np.random.normal(
                    loc=self.noise.get("mean", 0),
                    scale=self.noise.get("std", 1),
                    size=self.periods,
                )
            else:
                std = self.noise.get("std", 1)
                mean = self.noise.get("mean", 0)
                noise = np.random.uniform(
                    low=mean - std,
                    high=mean + std,
                    size=self.periods,
                )

        return y + noise

    def _apply_seasonality(self, y: np.ndarray) -> np.ndarray:
        if not self.seasonality:
            return y

        season_map = {
            "minute": 60,
            "hour": 24,
            "day": 7,
            "week": 52,
            "month": 12,
        }

        seasonality = self.seasonality
        if not isinstance(seasonality, list):
            seasonality = [seasonality]

        t = np.arange(self.periods)

        for s in seasonality:
            if isinstance(s, str):
                period = season_map[s]
                amplitude = 10
            else:
                period = season_map[s["type"]]
                amplitude = s["amplitude"]

            y += amplitude * np.sin(2 * np.pi * t / period)

        return y

    def _inject_anomalies(self, y: np.ndarray) -> np.ndarray:
        if not self.anomalies:
            return y
        count = self.anomalies.get("count")
        if not count:
            percentage = self.anomalies.get("percentage", 0)
            count = int(self.periods * percentage)

        idx = np.random.choice(self.periods, count, replace=False)
        magnitude = self.anomalies["magnitude"]
        anomaly_type = self.anomalies["type"]

        if anomaly_type == "spike":
            y[idx] *= 1 + magnitude
        elif anomaly_type == "dip":
            y[idx] *= 1 - magnitude
        elif anomaly_type == "shift":
            y[idx:] += magnitude
        elif anomaly_type == "outlier":
            y[idx] = y[idx] + np.random.normal(0, magnitude * 10, size=count)

        return y

    def _inject_missing(self, y: np.ndarray) -> np.ndarray:
        if not self.missing:
            return y

        prob = self.missing

        missing_idx = np.random.rand(self.periods) < prob
        y[missing_idx] = np.nan
        return y

    def _apply_constraints(self, y: np.ndarray) -> np.ndarray:
        if self.min_value is not None:
            y = np.maximum(y, self.min_value)
        if self.max_value is not None:
            y = np.minimum(y, self.max_value)
        return y

    def _set_seed(self):
        if self.seed is not None:
            np.random.seed(self.seed)

    def _format_output(self, t: List[datetime], y: np.ndarray) -> List[tuple]:
        return list(zip(t, y))

    def generate(self):
        self._set_seed()
        t = self._generate_time_index()
        y = self._generate_baseline()
        y = self._apply_trend(y)
        y = self._apply_noise(y)
        y = self._apply_seasonality(y)
        y = self._inject_anomalies(y)
        y = self._inject_missing(y)
        y = self._apply_constraints(y)

        return self._format_output(t, y)
