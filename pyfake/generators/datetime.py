from datetime import date, datetime, timedelta, time, timezone as dt_timezone
from pyfake.core.context import Context
from typing import Optional, Union
from zoneinfo import ZoneInfo


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

    min_date = ge if ge is not None else (gt + timedelta(days=1) if gt is not None else date(1970, 1, 1))
    max_date = le if le is not None else (lt - timedelta(days=1) if lt is not None else date(2100, 12, 31))

    delta_days = (max_date - min_date).days
    random_days = context.random.randint(0, delta_days)

    return min_date + timedelta(days=random_days)


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

    min_datetime = ge if ge is not None else (gt + timedelta(seconds=1) if gt is not None else datetime(1970, 1, 1))
    max_datetime = (
        le if le is not None else (lt - timedelta(seconds=1) if lt is not None else datetime(2100, 12, 31, 23, 59, 59))
    )

    delta_seconds = int((max_datetime - min_datetime).total_seconds())
    random_seconds = context.random.randint(0, delta_seconds)

    result = min_datetime + timedelta(seconds=random_seconds)

    if timezone is not None:
        result = result.replace(tzinfo=timezone)

    return result


def generate_time(
    *,
    gt: Optional[time] = None,
    lt: Optional[time] = None,
    ge: Optional[time] = None,
    le: Optional[time] = None,
    context: Optional[Context] = None,
    **kwargs,
) -> datetime.time:
    """
    Generate a random time object, given optional bounds.
    """

    if context is None:
        context = Context()

    min_time = ge if ge is not None else (gt.replace(second=gt.second + 1) if gt is not None else time(0, 0, 0))
    max_time = le if le is not None else (lt.replace(second=lt.second - 1) if lt is not None else time(23, 59, 59))

    min_seconds = min_time.hour * 3600 + min_time.minute * 60 + min_time.second
    max_seconds = max_time.hour * 3600 + max_time.minute * 60 + max_time.second

    random_seconds = context.random.randint(min_seconds, max_seconds)

    hours = random_seconds // 3600
    minutes = (random_seconds % 3600) // 60
    seconds = random_seconds % 60

    return time(hours, minutes, seconds)
