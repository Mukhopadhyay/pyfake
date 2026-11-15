import pytest
from datetime import date, datetime, timedelta, time as dt_time, timezone as dt_timezone
from zoneinfo import ZoneInfo

from pyfake.core.context import Context
from pyfake.generators import datetime as gen_dt


@pytest.mark.datatypes
# @pytest.mark.xfail
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
# @pytest.mark.xfail
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
# @pytest.mark.xfail
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


@pytest.mark.datatypes
@pytest.mark.datetime
class TestDatetimeContextDefault:
    """Tests that datetime generators work when context=None (default Context is created)."""

    def test_generate_date_no_context(self):
        result = gen_dt.generate_date()
        assert isinstance(result, date)
        assert date(1970, 1, 1) <= result <= date(2100, 12, 31)

    def test_generate_datetime_no_context(self):
        result = gen_dt.generate_datetime()
        assert isinstance(result, datetime)
        assert datetime(1970, 1, 1) <= result <= datetime(2100, 12, 31, 23, 59, 59)


@pytest.mark.datatypes
@pytest.mark.datetime
class TestGenerateDatetimeTimezone:
    """Tests for timezone (tzinfo) support in generate_datetime."""

    @pytest.mark.parametrize(
        "tz",
        [
            dt_timezone.utc,
            ZoneInfo("UTC"),
            ZoneInfo("America/New_York"),
            ZoneInfo("Europe/London"),
            ZoneInfo("Asia/Tokyo"),
        ],
    )
    def test_timezone_is_attached(self, tz):
        ctx = Context(seed=42)
        result = gen_dt.generate_datetime(timezone=tz, context=ctx)
        assert isinstance(result, datetime)
        assert result.tzinfo is tz

    def test_no_timezone_returns_naive(self):
        result = gen_dt.generate_datetime(context=Context(seed=1))
        assert result.tzinfo is None

    def test_timezone_with_bounds(self):
        tz = ZoneInfo("UTC")
        ge = datetime(2020, 1, 1)
        le = datetime(2020, 12, 31, 23, 59, 59)
        result = gen_dt.generate_datetime(ge=ge, le=le, timezone=tz, context=Context(seed=7))
        assert result.tzinfo is tz
        # Compare the naive part of the result against the bounds
        naive = result.replace(tzinfo=None)
        assert ge <= naive <= le

    def test_timezone_deterministic_with_seed(self):
        tz = ZoneInfo("Europe/London")
        a = gen_dt.generate_datetime(timezone=tz, context=Context(seed=99))
        b = gen_dt.generate_datetime(timezone=tz, context=Context(seed=99))
        assert a == b
        assert a.tzinfo is tz

    def test_generate_date_ignores_timezone_kwarg(self):
        # date has no tzinfo; timezone kwarg must be silently absorbed via **kwargs
        tz = ZoneInfo("UTC")
        result = gen_dt.generate_date(timezone=tz, context=Context(seed=1))
        assert isinstance(result, date)
        assert not isinstance(result, datetime)

    def test_generate_time_ignores_timezone_kwarg(self):
        # time without tzinfo; timezone kwarg must be silently absorbed via **kwargs
        tz = ZoneInfo("UTC")
        result = gen_dt.generate_time(timezone=tz, context=Context(seed=1))
        assert isinstance(result, dt_time)
        assert result.tzinfo is None


@pytest.mark.datatypes
@pytest.mark.datetime
class TestOneSidedDateBounds:
    """A single bound outside the default 1970-2100 window moves the window next to it."""

    @pytest.mark.parametrize("seed", list(range(10)) + [None])
    def test_date_lower_bound_after_default_range(self, seed):
        result = gen_dt.generate_date(ge=date(2200, 1, 1), context=Context(seed=seed))
        assert result >= date(2200, 1, 1)

    @pytest.mark.parametrize("seed", list(range(10)) + [None])
    def test_date_upper_bound_before_default_range(self, seed):
        result = gen_dt.generate_date(lt=date(1900, 1, 1), context=Context(seed=seed))
        assert result < date(1900, 1, 1)

    def test_date_near_min_is_clamped(self):
        result = gen_dt.generate_date(le=date(5, 1, 1), context=Context(seed=1))
        assert date.min <= result <= date(5, 1, 1)

    def test_date_near_max_is_clamped(self):
        result = gen_dt.generate_date(ge=date(9990, 1, 1), context=Context(seed=1))
        assert date(9990, 1, 1) <= result <= date.max

    @pytest.mark.parametrize("seed", list(range(10)) + [None])
    def test_datetime_one_sided_bounds(self, seed):
        assert gen_dt.generate_datetime(gt=datetime(2200, 1, 1), context=Context(seed=seed)) > datetime(2200, 1, 1)
        assert gen_dt.generate_datetime(le=datetime(1900, 1, 1), context=Context(seed=seed)) <= datetime(1900, 1, 1)

    def test_datetime_aware_bounds(self):
        ge = datetime(2020, 1, 1, tzinfo=dt_timezone.utc)
        result = gen_dt.generate_datetime(ge=ge, context=Context(seed=4))
        assert result.tzinfo is not None
        assert result >= ge

    def test_datetime_aware_bounds_converted_to_timezone(self):
        ge = datetime(2020, 1, 1, tzinfo=dt_timezone.utc)
        le = datetime(2020, 1, 2, tzinfo=dt_timezone.utc)
        tz = ZoneInfo("Asia/Tokyo")
        result = gen_dt.generate_datetime(ge=ge, le=le, timezone=tz, context=Context(seed=4))
        assert result.tzinfo is tz
        assert ge <= result <= le


@pytest.mark.datatypes
@pytest.mark.datetime
class TestGenerateTimeEdges:

    @pytest.mark.parametrize("seed", list(range(10)) + [None])
    def test_gt_at_second_59(self, seed):
        result = gen_dt.generate_time(gt=dt_time(12, 0, 59), context=Context(seed=seed))
        assert result > dt_time(12, 0, 59)

    @pytest.mark.parametrize("seed", list(range(10)) + [None])
    def test_lt_at_second_0(self, seed):
        result = gen_dt.generate_time(lt=dt_time(12, 0, 0), context=Context(seed=seed))
        assert result < dt_time(12, 0, 0)

    def test_sub_second_bounds_round_inwards(self):
        for seed in range(20):
            result = gen_dt.generate_time(
                ge=dt_time(12, 0, 0, 500_000), le=dt_time(12, 0, 2), context=Context(seed=seed)
            )
            assert dt_time(12, 0, 0, 500_000) <= result <= dt_time(12, 0, 2)

    def test_conflicting_bounds_raise_invalid_constraints(self):
        from pyfake.exceptions import InvalidConstraints

        with pytest.raises(InvalidConstraints):
            gen_dt.generate_time(gt=dt_time(23, 59, 59), context=Context(seed=1))


@pytest.mark.datatypes
@pytest.mark.datetime
class TestRelativeDates:
    """PastDate, FutureDate, PastDatetime and FutureDatetime are generated relative to context.now."""

    def test_past_date(self):
        ctx_now = datetime(2026, 6, 15, tzinfo=dt_timezone.utc)
        for seed in range(50):
            result = gen_dt.generate_past_date(context=Context(seed=seed, now=ctx_now))
            assert result < date(2026, 6, 15)

    def test_future_date(self):
        ctx_now = datetime(2026, 6, 15, tzinfo=dt_timezone.utc)
        for seed in range(50):
            result = gen_dt.generate_future_date(context=Context(seed=seed, now=ctx_now))
            assert result > date(2026, 6, 15)

    def test_past_date_respects_user_bounds(self):
        for seed in range(50):
            result = gen_dt.generate_past_date(ge=date(2020, 1, 1), lt=date(2021, 1, 1), context=Context(seed=seed))
            assert date(2020, 1, 1) <= result < date(2021, 1, 1)

    def test_future_date_respects_user_bounds(self):
        for seed in range(50):
            result = gen_dt.generate_future_date(gt=date(2150, 1, 1), context=Context(seed=seed))
            assert result > date(2150, 1, 1)

    def test_past_and_future_datetimes(self):
        now = datetime.now(dt_timezone.utc)
        for seed in range(50):
            ctx = Context(seed=seed)
            past = gen_dt.generate_past_datetime(context=ctx)
            future = gen_dt.generate_future_datetime(context=ctx)
            assert past.tzinfo is not None and past < now
            assert future.tzinfo is not None and future > now

    def test_relative_datetime_naive_bounds_read_as_utc(self):
        result = gen_dt.generate_past_datetime(
            ge=datetime(2020, 1, 1), le=datetime(2020, 1, 2), context=Context(seed=1)
        )
        assert datetime(2020, 1, 1, tzinfo=dt_timezone.utc) <= result <= datetime(2020, 1, 2, tzinfo=dt_timezone.utc)

    def test_relative_datetime_timezone(self):
        tz = ZoneInfo("America/New_York")
        result = gen_dt.generate_future_datetime(lt=datetime(2200, 1, 1), timezone=tz, context=Context(seed=2))
        assert result.tzinfo is tz

    def test_aware_datetime_defaults_to_utc(self):
        result = gen_dt.generate_aware_datetime(context=Context(seed=1))
        assert result.tzinfo is dt_timezone.utc

    def test_same_seed_same_output(self):
        assert gen_dt.generate_past_datetime(context=Context(seed=7)) == gen_dt.generate_past_datetime(
            context=Context(seed=7)
        )


@pytest.mark.datatypes
@pytest.mark.datetime
class TestGenerateTimedelta:

    @pytest.mark.parametrize("seed", list(range(10)) + [None])
    def test_default_range(self, seed):
        result = gen_dt.generate_timedelta(context=Context(seed=seed))
        assert timedelta(0) <= result <= timedelta(days=30)

    def test_bounds(self):
        for seed in range(50):
            result = gen_dt.generate_timedelta(
                gt=timedelta(hours=1), lt=timedelta(hours=2), context=Context(seed=seed)
            )
            assert timedelta(hours=1) < result < timedelta(hours=2)

    def test_negative_one_sided_bound(self):
        result = gen_dt.generate_timedelta(le=timedelta(days=-100), context=Context(seed=1))
        assert result <= timedelta(days=-100)

    @pytest.mark.parametrize(
        "generator",
        [
            gen_dt.generate_past_date,
            gen_dt.generate_future_date,
            gen_dt.generate_past_datetime,
            gen_dt.generate_future_datetime,
            gen_dt.generate_aware_datetime,
            gen_dt.generate_timedelta,
        ],
    )
    def test_no_context_creates_one(self, generator):
        assert generator() is not None
