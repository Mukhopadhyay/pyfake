import math
from datetime import date, datetime, timedelta, time, timezone as dt_timezone
from pyfake.core.context import Context
from pyfake.generators.bounds import resolve_bounds, check_range
from typing import Optional, Union
from zoneinfo import ZoneInfo

ONE_DAY = timedelta(days=1)
ONE_SECOND = timedelta(seconds=1)


def generate_date(
    *,
    lt: Optional[date] = None,
    gt: Optional[date] = None,
    le: Optional[date] = None,
    ge: Optional[date] = None,
    context: Optional[Context] = None,
    **kwargs,
) -> date:
    """
    Generate a random date object within the specified bounds.
    Returns as datetime ISO 8601 string.
    """

    if context is None:
        context = Context()

    min_date = ge if ge is not None else (gt + ONE_DAY if gt is not None else None)
    max_date = le if le is not None else (lt - ONE_DAY if lt is not None else None)
    min_date, max_date = resolve_bounds(
        min_date,
        max_date,
        date(1970, 1, 1),
        date(2100, 12, 31),
        floor=date.min,
        ceiling=date.max,
    )
    check_range(min_date, max_date, "date")

    delta_days = (max_date - min_date).days
    random_days = context.random.randint(0, delta_days)

    return min_date + timedelta(days=random_days)


def generate_past_date(
    *,
    lt: Optional[date] = None,
    le: Optional[date] = None,
    context: Optional[Context] = None,
    **kwargs,
) -> date:
    """
    Generate a date before today, for `PastDate` fields. The two-day margin keeps the
    date in the past in every timezone.
    """

    if context is None:
        context = Context()

    latest = context.now.date() - 2 * ONE_DAY
    upper = _earliest(latest, le, lt - ONE_DAY if lt is not None else None)
    return generate_date(le=upper, context=context, **kwargs)


def generate_future_date(
    *,
    gt: Optional[date] = None,
    ge: Optional[date] = None,
    context: Optional[Context] = None,
    **kwargs,
) -> date:
    """
    Generate a date after today, for `FutureDate` fields. The two-day margin keeps the
    date in the future in every timezone.
    """

    if context is None:
        context = Context()

    earliest = context.now.date() + 2 * ONE_DAY
    lower = _latest(earliest, ge, gt + ONE_DAY if gt is not None else None)
    return generate_date(ge=lower, context=context, **kwargs)


def generate_datetime(
    *,
    lt: Optional[datetime] = None,
    gt: Optional[datetime] = None,
    le: Optional[datetime] = None,
    ge: Optional[datetime] = None,
    timezone: Optional[Union[dt_timezone, ZoneInfo]] = None,
    context: Optional[Context] = None,
    **kwargs,
) -> datetime:
    """
    Generate a random datetime object within the specified bounds.

    If *timezone* is provided (any :class:`datetime.tzinfo` subclass, e.g.
    ``datetime.timezone.utc`` or a ``zoneinfo.ZoneInfo`` instance), the
    returned datetime will have that timezone attached via
    ``replace(tzinfo=timezone)``.  Bounds (ge/gt/le/lt) are still evaluated
    as naive datetimes; the timezone is stamped on the result after generation.
    """

    if context is None:
        context = Context()

    min_datetime = (
        ge if ge is not None else (gt + ONE_SECOND if gt is not None else None)
    )
    max_datetime = (
        le if le is not None else (lt - ONE_SECOND if lt is not None else None)
    )

    # Timezone-aware bounds get timezone-aware defaults, so the two can be compared
    bounds_tz = next(
        (
            b.tzinfo
            for b in (min_datetime, max_datetime)
            if b is not None and b.tzinfo is not None
        ),
        None,
    )
    min_datetime, max_datetime = resolve_bounds(
        min_datetime,
        max_datetime,
        datetime(1970, 1, 1, tzinfo=bounds_tz),
        datetime(2100, 12, 31, 23, 59, 59, tzinfo=bounds_tz),
        floor=datetime.min.replace(tzinfo=bounds_tz),
        ceiling=datetime.max.replace(tzinfo=bounds_tz),
    )
    check_range(min_datetime, max_datetime, "datetime")

    delta_seconds = int((max_datetime - min_datetime).total_seconds())
    random_seconds = context.random.randint(0, delta_seconds)

    result = min_datetime + timedelta(seconds=random_seconds)

    if timezone is not None:
        # An aware result (from aware bounds) is converted, so it stays the same instant
        result = (
            result.astimezone(timezone)
            if result.tzinfo is not None
            else result.replace(tzinfo=timezone)
        )

    return result


def generate_aware_datetime(
    *,
    timezone: Optional[Union[dt_timezone, ZoneInfo]] = None,
    context: Optional[Context] = None,
    **kwargs,
) -> datetime:
    """
    Generate a timezone-aware datetime, for `AwareDatetime` fields. Uses UTC unless a timezone is given.
    """
    return generate_datetime(
        timezone=timezone or dt_timezone.utc, context=context, **kwargs
    )


def generate_past_datetime(
    *,
    lt: Optional[datetime] = None,
    gt: Optional[datetime] = None,
    le: Optional[datetime] = None,
    ge: Optional[datetime] = None,
    timezone: Optional[Union[dt_timezone, ZoneInfo]] = None,
    context: Optional[Context] = None,
    **kwargs,
) -> datetime:
    """
    Generate a timezone-aware datetime before now, for `PastDatetime` fields.
    Uses UTC unless a timezone is given. Naive bounds are read as UTC.
    """

    if context is None:
        context = Context()

    return _relative_datetime(
        earliest=None,
        latest=context.now - ONE_SECOND,
        lt=lt,
        gt=gt,
        le=le,
        ge=ge,
        timezone=timezone,
        context=context,
    )


def generate_future_datetime(
    *,
    lt: Optional[datetime] = None,
    gt: Optional[datetime] = None,
    le: Optional[datetime] = None,
    ge: Optional[datetime] = None,
    timezone: Optional[Union[dt_timezone, ZoneInfo]] = None,
    context: Optional[Context] = None,
    **kwargs,
) -> datetime:
    """
    Generate a timezone-aware datetime after now, for `FutureDatetime` fields.
    Uses UTC unless a timezone is given. Naive bounds are read as UTC.
    """

    if context is None:
        context = Context()

    # context.now defaults to the start of the current UTC day, so begin a day later
    return _relative_datetime(
        earliest=context.now + ONE_DAY + ONE_SECOND,
        latest=None,
        lt=lt,
        gt=gt,
        le=le,
        ge=ge,
        timezone=timezone,
        context=context,
    )


def _relative_datetime(
    *, earliest, latest, lt, gt, le, ge, timezone, context
) -> datetime:
    lower = _latest(
        earliest, _as_utc(ge), _as_utc(gt) + ONE_SECOND if gt is not None else None
    )
    upper = _earliest(
        latest, _as_utc(le), _as_utc(lt) - ONE_SECOND if lt is not None else None
    )
    result = generate_datetime(ge=lower, le=upper, context=context)
    return result.astimezone(timezone) if timezone is not None else result


def generate_time(
    *,
    gt: Optional[time] = None,
    lt: Optional[time] = None,
    ge: Optional[time] = None,
    le: Optional[time] = None,
    context: Optional[Context] = None,
    **kwargs,
) -> time:
    """
    Generate a random time object, given optional bounds.
    """

    if context is None:
        context = Context()

    # Work in whole seconds since midnight, so stepping past a bound can't overflow a field
    # (e.g. gt=time(12, 0, 59)). Sub-second bounds round inwards.
    min_seconds = (
        _seconds(ge, round_up=True)
        if ge is not None
        else (_seconds(gt) + 1 if gt is not None else 0)
    )
    max_seconds = (
        _seconds(le)
        if le is not None
        else (_seconds(lt, round_up=True) - 1 if lt is not None else 86399)
    )
    check_range(min_seconds, max_seconds, "time")

    random_seconds = context.random.randint(min_seconds, max_seconds)

    hours = random_seconds // 3600
    minutes = (random_seconds % 3600) // 60
    seconds = random_seconds % 60

    return time(hours, minutes, seconds)


def generate_timedelta(
    *,
    lt: Optional[timedelta] = None,
    gt: Optional[timedelta] = None,
    le: Optional[timedelta] = None,
    ge: Optional[timedelta] = None,
    context: Optional[Context] = None,
    **kwargs,
) -> timedelta:
    """
    Generate a random whole-second timedelta, between 0 and 30 days by default.
    """

    if context is None:
        context = Context()

    lower = ge if ge is not None else (gt + ONE_SECOND if gt is not None else None)
    upper = le if le is not None else (lt - ONE_SECOND if lt is not None else None)
    lower, upper = resolve_bounds(
        lower,
        upper,
        timedelta(0),
        timedelta(days=30),
        floor=timedelta.min,
        ceiling=timedelta.max,
    )

    min_seconds, max_seconds = math.ceil(lower.total_seconds()), math.floor(
        upper.total_seconds()
    )
    check_range(min_seconds, max_seconds, "timedelta")

    return timedelta(seconds=context.random.randint(min_seconds, max_seconds))


def _seconds(value: time, round_up: bool = False) -> int:
    seconds = value.hour * 3600 + value.minute * 60 + value.second
    return seconds + 1 if round_up and value.microsecond else seconds


def _as_utc(value: Optional[datetime]) -> Optional[datetime]:
    if value is not None and value.tzinfo is None:
        return value.replace(tzinfo=dt_timezone.utc)
    return value


def _earliest(*values):
    return min((v for v in values if v is not None), default=None)


def _latest(*values):
    return max((v for v in values if v is not None), default=None)
