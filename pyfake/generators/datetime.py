from datetime import date, datetime, timedelta, time
from pyfake.core.context import Context
from typing import Optional


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
    """

    if context is None:
        context = Context()

    min_date = (
        ge
        if ge is not None
        else (gt + timedelta(days=1) if gt is not None else date(1970, 1, 1))
    )
    max_date = (
        le
        if le is not None
        else (lt - timedelta(days=1) if lt is not None else date(2100, 12, 31))
    )

    delta_days = (max_date - min_date).days
    random_days = context.random.randint(0, delta_days)

    return min_date + timedelta(days=random_days)


def generate_datetime(
    *,
    lt: Optional[datetime] = None,
    gt: Optional[datetime] = None,
    le: Optional[datetime] = None,
    ge: Optional[datetime] = None,
    context: Optional[Context] = None,
    **kwargs,
) -> datetime:
    """
    Generate a random datetime object within the specified bounds.
    """

    if context is None:
        context = Context()

    min_datetime = (
        ge
        if ge is not None
        else (gt + timedelta(seconds=1) if gt is not None else datetime(1970, 1, 1))
    )
    max_datetime = (
        le
        if le is not None
        else (
            lt - timedelta(seconds=1)
            if lt is not None
            else datetime(2100, 12, 31, 23, 59, 59)
        )
    )

    delta_seconds = int((max_datetime - min_datetime).total_seconds())
    random_seconds = context.random.randint(0, delta_seconds)

    return min_datetime + timedelta(seconds=random_seconds)


def generate_time(*, context: Optional[Context] = None, **kwargs) -> datetime.time:
    """
    Generate a random time object.
    """
    return time(
        hour=context.random.randint(0, 23),
        minute=context.random.randint(0, 59),
        second=context.random.randint(0, 59),
        microsecond=context.random.randint(0, 999_999),
    )
