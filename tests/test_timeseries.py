from datetime import datetime

import numpy as np
import pytest

from pyfake import Timeseries


class TestTimeseriesClass:
    def test_instantiation(self):
        ts = Timeseries(start="2023-01-01", baseline=100.0, periods=10, freq="day")
        assert ts.start == datetime(2023, 1, 1)
        assert ts.baseline == 100.0

    def test_datetime_start(self):
        start_dt = datetime(2023, 1, 1)
        ts = Timeseries(start=start_dt, baseline=100.0, periods=10, freq="day")
        assert ts.start == start_dt
        assert ts.baseline == 100.0

    def test_timeseries_generation(self):
        ts = Timeseries(start="2023-01-01", baseline=100.0, periods=10, freq="day")
        data = ts.generate()
        assert isinstance(data, list)
        assert len(data) == 10

    def test_reproducibility(self):
        ts1 = Timeseries(
            start="2023-01-01", baseline=100.0, periods=10, freq="day", seed=42
        )
        ts2 = Timeseries(
            start="2023-01-01", baseline=100.0, periods=10, freq="day", seed=42
        )
        data1 = ts1.generate()
        data2 = ts2.generate()
        assert data1 == data2


class TestTimeseriesTrend:
    def test_trend_generation(self):
        ts = Timeseries(
            start="2023-01-01",
            baseline=100.0,
            periods=10,
            freq="day",
            trend={"type": "upward", "slope": 5},
        )
        data = ts.generate()
        assert data[0][1] == 100.0
        assert data[1][1] == 105.0
        assert data[2][1] == 110.0

    def test_no_explicit_trend_arg(self):
        ts = Timeseries(
            start="2023-01-01",
            baseline=100.0,
            periods=3,
            freq="day",
            trend=None,
        )
        data = ts.generate()

        assert data[0][1] == 100.0
        assert data[1][1] == 100.1
        assert data[2][1] == 100.2

    def test_trend_dict_arg(self):
        ts = Timeseries(
            start="2023-01-01",
            baseline=100.0,
            periods=10,
            freq="day",
            trend={"type": "downward", "slope": 3},
        )
        data = ts.generate()
        assert data[0][1] == 100.0
        assert data[1][1] == 97.0
        assert data[2][1] == 94.0

    def test_trend_flat(self):
        ts = Timeseries(
            start="2023-01-01",
            baseline=100.0,
            periods=10,
            freq="day",
            trend={"type": "flat", "slope": 5},
        )
        data = ts.generate()
        assert data[0][1] == 100.0
        assert data[1][1] == 100.0
        assert data[2][1] == 100.0


def _values(ts):
    return np.array([v for _, v in ts.generate()])


def _flat(**kwargs):
    params = dict(
        start="2023-01-01", baseline=100.0, periods=30, freq="day", trend="flat", seed=1
    )
    params.update(kwargs)
    return Timeseries(**params)


@pytest.mark.timeseries
class TestTimeseriesRandomState:
    def test_seed_does_not_touch_global_numpy_state(self):
        np.random.seed(0)
        expected = np.random.random()

        np.random.seed(0)
        _flat(
            noise=1.0,
            missing=0.1,
            anomalies={"type": "outlier", "count": 2, "magnitude": 1},
        ).generate()
        assert np.random.random() == expected

    def test_reproducible_with_noise_and_anomalies(self):
        params = dict(
            noise=2.0,
            seasonality="day",
            anomalies={"type": "spike", "count": 3, "magnitude": 0.5},
        )
        assert np.array_equal(_values(_flat(**params)), _values(_flat(**params)))

    def test_generate_twice_gives_the_same_series(self):
        ts = _flat(noise=1.0)
        assert np.array_equal(_values(ts), _values(ts))

    def test_different_seeds_differ(self):
        assert not np.array_equal(
            _values(_flat(noise=1.0, seed=1)), _values(_flat(noise=1.0, seed=2))
        )


@pytest.mark.timeseries
class TestTimeseriesNoise:
    def test_float_noise(self):
        values = _values(_flat(noise=1.0, periods=500))
        assert 0.5 < np.std(values) < 1.5

    def test_normal_noise_dict(self):
        values = _values(
            _flat(noise={"distribution": "normal", "mean": 5, "std": 1}, periods=500)
        )
        assert 104 < np.mean(values) < 106

    def test_uniform_noise_dict(self):
        values = _values(
            _flat(noise={"distribution": "uniform", "mean": 0, "std": 2}, periods=500)
        )
        assert np.all((values >= 98) & (values <= 102))


@pytest.mark.timeseries
class TestTimeseriesSeasonality:
    def test_string_seasonality(self):
        values = _values(_flat(seasonality="day", periods=14))
        # Weekly cycle with amplitude 10
        assert np.isclose(values[0], values[7])
        assert np.isclose(values.max() - 100, 10, atol=1)

    def test_dict_and_list_seasonality(self):
        values = _values(
            _flat(seasonality=[{"type": "day", "amplitude": 3}, "hour"], periods=50)
        )
        assert not np.allclose(values, 100)


@pytest.mark.timeseries
class TestTimeseriesAnomalies:
    def test_spike(self):
        values = _values(
            _flat(anomalies={"type": "spike", "count": 2, "magnitude": 0.5})
        )
        assert sorted(values)[-2:] == [150.0, 150.0]

    def test_dip(self):
        values = _values(_flat(anomalies={"type": "dip", "count": 2, "magnitude": 0.5}))
        assert sorted(values)[:2] == [50.0, 50.0]

    def test_percentage(self):
        values = _values(
            _flat(anomalies={"type": "spike", "percentage": 0.1, "magnitude": 1})
        )
        assert np.count_nonzero(values == 200.0) == 3

    def test_shift(self):
        values = _values(
            _flat(anomalies={"type": "shift", "count": 2, "magnitude": 10})
        )
        # Two level shifts: the series steps up twice and never comes back down
        assert set(np.unique(values)) <= {100.0, 110.0, 120.0}
        assert values[-1] == 120.0
        assert np.all(np.diff(values) >= 0)

    def test_outlier(self):
        values = _values(
            _flat(anomalies={"type": "outlier", "count": 3, "magnitude": 1})
        )
        assert np.count_nonzero(values != 100.0) == 3

    @pytest.mark.parametrize("seasonality,period", [(None, 7), ("hour", 24)])
    def test_seasonal_anomaly(self, seasonality, period):
        anomalies = {
            "type": "seasonal_anomaly",
            "count": 1,
            "magnitude": 5,
            "seasonality": seasonality,
        }
        values = _values(_flat(periods=60, anomalies=anomalies))
        changed = np.flatnonzero(~np.isclose(values, 100.0))
        assert changed.size > 0
        # One cycle of the injected wave, at most `period` long, with amplitude `magnitude`
        assert changed[-1] - changed[0] < period
        assert np.abs(values - 100).max() <= 5 + 1e-9

    def test_unknown_anomaly_raises(self):
        with pytest.raises(ValueError, match="Unknown anomaly type"):
            _flat(anomalies={"type": "wobble", "count": 1, "magnitude": 1}).generate()


@pytest.mark.timeseries
class TestTimeseriesMissingAndConstraints:
    def test_missing(self):
        values = _values(_flat(missing=0.3, periods=200))
        assert 20 < np.count_nonzero(np.isnan(values)) < 100

    def test_min_and_max_value(self):
        values = _values(_flat(noise=20.0, min_value=90, max_value=110, periods=200))
        assert values.min() == 90 and values.max() == 110
