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
