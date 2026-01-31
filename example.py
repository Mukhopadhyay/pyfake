import warnings

warnings.filterwarnings("ignore")

from pyfake import Pyfake
from rich import print

from pydantic import UUID1, UUID3, UUID4, UUID5, UUID6, UUID7, UUID8
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Annotated, Union
from datetime import datetime, date, timezone, time


class Model(BaseModel):
    """
    Exhaustive date & datetime coverage for pyfake.
    """

    plain_date: date
    plain_datetime: datetime

    optional_date: Optional[date] = None
    optional_datetime: Optional[datetime] = None

    nullable_date: Optional[date] = None
    nullable_datetime: Optional[datetime] = None

    date_with_default: date = Field(default_factory=date.today)
    datetime_with_default: datetime = Field(default_factory=datetime.now)

    utc_datetime_default: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    naive_datetime: datetime
    aware_datetime: datetime

    offset_datetime: datetime = Field(description="Datetime with fixed offset tzinfo")

    date_with_time: datetime
    time_only: time

    past_date: Annotated[date, Field(description="Should be before today")]

    future_datetime: Annotated[datetime, Field(description="Should be in the future")]

    min_max_date: Annotated[date, Field(ge=date(1970, 1, 1), le=date(2100, 12, 31))]

    min_max_datetime: Annotated[
        datetime,
        Field(
            ge=datetime(1970, 1, 1, tzinfo=timezone.utc),
            le=datetime(2100, 12, 31, tzinfo=timezone.utc),
        ),
    ]

    date_from_string: date
    datetime_from_string: datetime

    iso_datetime_z: datetime = Field(description="ISO 8601 with Z suffix")

    date_or_datetime: Union[date, datetime]

    flexible_datetime: Union[
        datetime,
        int,  # unix timestamp (seconds)
        float,  # unix timestamp (float)
        str,  # ISO string
    ]


x = Pyfake.from_schema(Model, num=1, as_dict=False)
print(x)
