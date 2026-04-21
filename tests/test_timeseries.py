from pyfake import Timeseries
from datetime import datetime


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
        ts1 = Timeseries(start="2023-01-01", baseline=100.0, periods=10, freq="day", seed=42)
        ts2 = Timeseries(start="2023-01-01", baseline=100.0, periods=10, freq="day", seed=42)
        data1 = ts1.generate()
        data2 = ts2.generate()
        assert data1 == data2


class TestTimeseriesTrend:
    def test_trend_generation(self):
        ts = Timeseries(
            start="2023-01-01", baseline=100.0, periods=10, freq="day", trend={"type": "upward", "slope": 5}
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
