import pytest
from datetime import date, datetime, timedelta, time as dt_time

from pyfake.core.context import Context
from pyfake.generators import datetime as gen_dt


@pytest.mark.datatypes
@pytest.mark.xfail
@pytest.mark.datetime
class TestGenerateDate:

    def test_type_and_default_bounds(self):
        ctx = Context(seed=42)
        result = gen_dt.generate_date(context=ctx)
        assert isinstance(result, date)
        assert date(1970, 1, 1) <= result <= date(2100, 12, 31)

    @pytest.mark.parametrize(
        "lt,gt,le,ge",
        [
            (date(2025, 1, 1), date(2024, 12, 1), None, None),
            (None, None, date(2023, 6, 1), date(2023, 1, 1)),
            (date(2021, 6, 1), date(2021, 1, 1), date(2021, 6, 15), date(2021, 1, 15)),
            (None, None, None, None),
        ],
    )
    def test_bounds_respected(self, lt, gt, le, ge):
        ctx = Context(seed=7)
        result = gen_dt.generate_date(lt=lt, gt=gt, le=le, ge=ge, context=ctx)
        if ge is not None:
            assert result >= ge
        if gt is not None:
            assert result > gt
        if le is not None:
            assert result <= le
        if lt is not None:
            assert result < lt

    def test_single_day_interval_returns_that_day(self):
        # When min == max, should return that single date
        single = date(2000, 2, 29)
        result = gen_dt.generate_date(ge=single, le=single, context=Context(seed=1))
        assert result == single

    def test_conflicting_bounds_raise(self):
        # Construct gt and lt such that min_date > max_date -> randint will fail
        gt = date(2020, 1, 3)
        lt = date(2020, 1, 3)
        with pytest.raises(ValueError):
            gen_dt.generate_date(gt=gt, lt=lt, context=Context(seed=2))

    def test_deterministic_with_seed(self):
        a = gen_dt.generate_date(context=Context(seed=12345))
        b = gen_dt.generate_date(context=Context(seed=12345))
        assert a == b


@pytest.mark.datatypes
@pytest.mark.xfail
@pytest.mark.datetime
class TestGenerateDatetime:

    def test_type_and_default_bounds(self):
        ctx = Context(seed=99)
        result = gen_dt.generate_datetime(context=ctx)
        assert isinstance(result, datetime)
        assert datetime(1970, 1, 1) <= result <= datetime(2100, 12, 31, 23, 59, 59)

    @pytest.mark.parametrize(
        "lt,gt,le,ge",
        [
            (datetime(2025, 1, 1), datetime(2024, 12, 1), None, None),
            (None, None, datetime(2023, 6, 1, 12), datetime(2023, 1, 1, 8)),
            (
                datetime(2021, 6, 1, 0, 0, 30),
                datetime(2021, 1, 1, 0, 0, 15),
                datetime(2021, 6, 15, 23, 59, 59),
                datetime(2021, 1, 15, 12, 0, 0),
            ),
            (None, None, None, None),
        ],
    )
    def test_bounds_respected(self, lt, gt, le, ge):
        ctx = Context(seed=13)
        result = gen_dt.generate_datetime(lt=lt, gt=gt, le=le, ge=ge, context=ctx)
        if ge is not None:
            assert result >= ge
        if gt is not None:
            assert result > gt
        if le is not None:
            assert result <= le
        if lt is not None:
            assert result < lt

    def test_single_datetime_interval_returns_exact(self):
        exact = datetime(2010, 10, 10, 10, 10, 10)
        result = gen_dt.generate_datetime(ge=exact, le=exact, context=Context(seed=5))
        assert result == exact

    def test_conflicting_datetime_bounds_raise(self):
        gt = datetime(2020, 1, 3, 0, 0, 1)
        lt = datetime(2020, 1, 3, 0, 0, 1)
        with pytest.raises(ValueError):
            gen_dt.generate_datetime(gt=gt, lt=lt, context=Context(seed=6))

    def test_deterministic_with_seed(self):
        a = gen_dt.generate_datetime(context=Context(seed=2026))
        b = gen_dt.generate_datetime(context=Context(seed=2026))
        assert a == b


@pytest.mark.datatypes
@pytest.mark.datetime
@pytest.mark.xfail
class TestGenerateTime:
    def test_context_optional_returns_time(self):
        # The implementation now defaults a Context when none is provided
        t = gen_dt.generate_time()
        assert isinstance(t, dt_time)

    def test_components_in_range(self):
        ctx = Context(seed=7)
        t = gen_dt.generate_time(context=ctx)
        assert isinstance(t, dt_time)
        assert 0 <= t.hour <= 23
        assert 0 <= t.minute <= 59
        assert 0 <= t.second <= 59
        assert 0 <= t.microsecond <= 999_999

    def test_deterministic_with_seed(self):
        t1 = gen_dt.generate_time(context=Context(seed=42))
        t2 = gen_dt.generate_time(context=Context(seed=42))
        assert t1 == t2

    @pytest.mark.parametrize(
        "lt,gt,le,ge",
        [
            (dt_time(23, 59, 59), dt_time(0, 0, 0), None, None),
            (None, None, dt_time(12, 30, 0), dt_time(8, 15, 0)),
            (
                dt_time(18, 0, 0),
                dt_time(9, 0, 0),
                dt_time(18, 30, 0),
                dt_time(9, 15, 0),
            ),
            (None, None, None, None),
        ],
    )
    def test_bounds_respected(self, lt, gt, le, ge):
        ctx = Context(seed=13)
        result = gen_dt.generate_time(lt=lt, gt=gt, le=le, ge=ge, context=ctx)
        if ge is not None:
            assert result >= ge
        if gt is not None:
            assert result > gt
        if le is not None:
            assert result <= le
        if lt is not None:
            assert result < lt

    def test_conflicting_time_bounds_raise(self):
        # Set gt and lt such that min_time > max_time -> randint will fail
        gt = dt_time(12, 0, 0)
        lt = dt_time(12, 0, 0)
        with pytest.raises(ValueError):
            gen_dt.generate_time(gt=gt, lt=lt, context=Context(seed=2))
