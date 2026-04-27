import pytest
from pyfake import Pyfake
from pydantic import BaseModel, Field
from typing import Annotated, Optional
from datetime import date, datetime, time, timezone as dt_timezone
from zoneinfo import ZoneInfo


@pytest.mark.datatypes
@pytest.mark.datetime
# @pytest.mark.xfail
class TestPyfakeDateTimeGeneration:

    class StressTestDateModel(BaseModel):
        date_basic: date
        date_optional: Optional[date]
        date_with_bounds: Annotated[date, Field(ge=date(2000, 1, 1), le=date(2020, 12, 31))]
        date_with_gt_lt: Annotated[date, Field(gt=date(2010, 1, 1), lt=date(2010, 1, 10))]
        date_optional_default: Optional[Annotated[date, Field(ge=date(1990, 1, 1), default=date(1995, 5, 5))]] = None

    @pytest.mark.parametrize(
        "seed",
        list(range(10)) + [None],
    )
    def test_date_generation(self, seed):
        pyfake = Pyfake(self.StressTestDateModel, seed=seed)
        result = pyfake.generate()

        assert isinstance(result, dict)
        assert isinstance(result["date_basic"], date)
        assert isinstance(result["date_optional"], (date, type(None)))

        assert date(2000, 1, 1) <= result["date_with_bounds"] <= date(2020, 12, 31)
        assert date(2010, 1, 1) < result["date_with_gt_lt"] < date(2010, 1, 10)
        if result["date_optional_default"] is not None:
            assert result["date_optional_default"] == date(1995, 5, 5) or result["date_optional_default"] >= date(
                1990, 1, 1
            )

    class StressTestDatetimeModel(BaseModel):
        datetime_basic: datetime
        datetime_optional: Optional[datetime]
        datetime_with_bounds: Annotated[
            datetime,
            Field(ge=datetime(2000, 1, 1, 0, 0, 0), le=datetime(2000, 12, 31, 23, 59, 59)),
        ]
        datetime_with_gt_lt: Annotated[
            datetime,
            Field(gt=datetime(2020, 1, 1, 0, 0, 0), lt=datetime(2020, 1, 1, 0, 0, 10)),
        ]
        datetime_with_defaults: Annotated[
            datetime,
            Field(
                ge=datetime(2010, 1, 1),
                le=datetime(2010, 1, 2),
                default=datetime(2010, 1, 1, 12, 0, 0),
            ),
        ] = datetime(2010, 1, 1, 13, 0, 0)

    @pytest.mark.parametrize(
        "seed",
        list(range(10)) + [None],
    )
    def test_datetime_generation(self, seed):
        pyfake = Pyfake(self.StressTestDatetimeModel, seed=seed)
        result = pyfake.generate()

        assert isinstance(result, dict)
        assert isinstance(result["datetime_basic"], datetime)
        assert isinstance(result["datetime_optional"], (datetime, type(None)))

        assert datetime(2000, 1, 1, 0, 0, 0) <= result["datetime_with_bounds"] <= datetime(2000, 12, 31, 23, 59, 59)
        assert datetime(2020, 1, 1, 0, 0, 0) < result["datetime_with_gt_lt"] < datetime(2020, 1, 1, 0, 0, 10)
        if result["datetime_with_defaults"] is not None:
            assert result["datetime_with_defaults"] == datetime(2010, 1, 1, 13, 0, 0) or (
                datetime(2010, 1, 1) <= result["datetime_with_defaults"] <= datetime(2010, 1, 2)
            )

    class StressTestTimeModel(BaseModel):
        time_basic: time
        time_optional: Optional[time]
        time_with_bounds: Annotated[time, Field(ge=time(1, 0, 0), le=time(5, 0, 0))]
        time_with_gt_lt: Annotated[time, Field(gt=time(10, 0, 0), lt=time(10, 0, 10))]
        time_optional_default: Optional[Annotated[time, Field(default=time(12, 0, 0))]] = None

    @pytest.mark.parametrize(
        "seed",
        list(range(10)) + [None],
    )
    def test_time_generation(self, seed):
        pyfake = Pyfake(self.StressTestTimeModel, seed=seed)
        result = pyfake.generate()

        assert isinstance(result, dict)
        assert isinstance(result["time_basic"], time)
        assert isinstance(result["time_optional"], (time, type(None)))

        assert (
            (1, 0, 0)
            <= (
                result["time_with_bounds"].hour,
                result["time_with_bounds"].minute,
                result["time_with_bounds"].second,
            )
            <= (5, 0, 0)
        )
        hour, minute, second = (
            result["time_with_gt_lt"].hour,
            result["time_with_gt_lt"].minute,
            result["time_with_gt_lt"].second,
        )
        assert (10, 0, 0) < (hour, minute, second) < (10, 0, 10)
        if result["time_optional_default"] is not None:
            assert result["time_optional_default"] == time(12, 0, 0) or isinstance(
                result["time_optional_default"], time
            )

    def test_time_gt_second_59_raises(self):
        # The generator implementation increments gt.second which can be invalid for second==59.
        class Model(BaseModel):
            t: Annotated[time, Field(gt=time(12, 0, 59))]

        pyfake = Pyfake(Model)
        with pytest.raises(Exception):
            pyfake.generate()


@pytest.mark.datatypes
@pytest.mark.datetime
class TestPyfakeDateTimeBareAnnotation:
    """Bare datetime/date/time annotations (no Field) must resolve through _type_map."""

    class BareModel(BaseModel):
        joined_at: datetime
        birthday: date
        alarm: time
        last_seen: Optional[datetime]

    @pytest.mark.parametrize("seed", list(range(10)) + [None])
    def test_bare_datetime_types(self, seed):
        result = Pyfake(self.BareModel, seed=seed).generate()

        assert isinstance(result, dict)
        assert isinstance(result["joined_at"], datetime)
        assert isinstance(result["birthday"], date)
        assert isinstance(result["alarm"], time)
        assert isinstance(result["last_seen"], (datetime, type(None)))


@pytest.mark.datatypes
@pytest.mark.datetime
class TestPyfakeDatetimeTimezone:
    """Integration tests for timezone support via json_schema_extra."""

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
    def test_timezone_attached_via_json_schema_extra(self, tz):
        class Model(BaseModel):
            ts: Annotated[datetime, Field(..., json_schema_extra={"timezone": tz})]

        result = Pyfake(Model, seed=42).generate()
        assert isinstance(result["ts"], datetime)
        assert result["ts"].tzinfo is tz

    @pytest.mark.parametrize("seed", list(range(5)) + [None])
    def test_timezone_utc_stdlib(self, seed):
        class Model(BaseModel):
            ts: Annotated[datetime, Field(..., json_schema_extra={"timezone": dt_timezone.utc})]

        result = Pyfake(Model, seed=seed).generate()
        assert result["ts"].tzinfo is dt_timezone.utc

    def test_timezone_with_bounds(self):
        tz = ZoneInfo("UTC")

        class Model(BaseModel):
            ts: Annotated[
                datetime,
                Field(
                    ge=datetime(2020, 1, 1),
                    le=datetime(2020, 12, 31, 23, 59, 59),
                    json_schema_extra={"timezone": tz},
                ),
            ]

        for seed in range(10):
            result = Pyfake(Model, seed=seed).generate()
            ts = result["ts"]
            assert ts.tzinfo is tz
            naive = ts.replace(tzinfo=None)
            assert datetime(2020, 1, 1) <= naive <= datetime(2020, 12, 31, 23, 59, 59)

    def test_optional_datetime_with_timezone(self):
        tz = ZoneInfo("America/New_York")

        class Model(BaseModel):
            ts: Optional[Annotated[datetime, Field(..., json_schema_extra={"timezone": tz})]]

        # Run enough times to get both None and non-None results
        results = [Pyfake(Model, seed=s).generate()["ts"] for s in range(30)]
        non_none = [r for r in results if r is not None]
        assert len(non_none) > 0
        for ts in non_none:
            assert ts.tzinfo is tz

    def test_multiple_timezone_fields(self):
        class Model(BaseModel):
            utc_ts: Annotated[datetime, Field(..., json_schema_extra={"timezone": ZoneInfo("UTC")})]
            ny_ts: Annotated[datetime, Field(..., json_schema_extra={"timezone": ZoneInfo("America/New_York")})]
            naive_ts: datetime

        result = Pyfake(Model, seed=1).generate()
        assert result["utc_ts"].tzinfo == ZoneInfo("UTC")
        assert result["ny_ts"].tzinfo == ZoneInfo("America/New_York")
        assert result["naive_ts"].tzinfo is None

    def test_no_timezone_remains_naive(self):
        class Model(BaseModel):
            ts: datetime

        result = Pyfake(Model, seed=7).generate()
        assert result["ts"].tzinfo is None

    def test_date_and_time_unaffected_by_timezone_kwarg(self):
        # Passing timezone via json_schema_extra on date/time fields must not crash;
        # date and time generators absorb it silently via **kwargs.
        class Model(BaseModel):
            d: Annotated[date, Field(..., json_schema_extra={"timezone": ZoneInfo("UTC")})]
            t: Annotated[time, Field(..., json_schema_extra={"timezone": ZoneInfo("UTC")})]

        result = Pyfake(Model, seed=5).generate()
        assert isinstance(result["d"], date)
        assert isinstance(result["t"], time)
