from datetime import date, datetime, time
from typing import Annotated, Optional, List, Dict
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, EmailStr, HttpUrl


class StressTestModel(BaseModel):
    # -------------------------
    # Basic primitives
    # -------------------------

    integer_basic: int
    integer_with_bounds: Annotated[int, Field(ge=1, le=100)]
    integer_optional: Optional[int]
    integer_optional_default: Optional[int] = 42

    float_basic: float
    float_with_bounds: Annotated[float, Field(gt=0.0, lt=1.0)]

    boolean_basic: bool
    boolean_default: bool = True

    string_basic: str
    string_with_length: Annotated[str, Field(min_length=5, max_length=20)]
    string_regex: Annotated[str, Field(pattern=r"^[a-z]{3}[0-9]{2}$")]
    string_default: str = "default_value"

    # -------------------------
    # Common real-world types
    # -------------------------

    uuid_value: UUID
    uuid_default: UUID = Field(default_factory=uuid4)

    email: EmailStr
    website: HttpUrl

    # -------------------------
    # Date & time types
    # -------------------------

    datetime_basic: datetime
    datetime_past: Annotated[datetime, Field(le=datetime.now())]

    date_basic: date
    date_future: Annotated[date, Field(gt=date.today())]

    time_basic: time

    # -------------------------
    # Collections
    # -------------------------

    int_list: List[int]
    bounded_list: Annotated[List[int], Field(min_length=1, max_length=5)]

    nested_list: List[List[str]]

    string_dict: Dict[str, str]
    mixed_dict: Dict[str, int]

    # -------------------------
    # Optional + nullable combos
    # -------------------------

    nullable_string: Optional[str] = None
    nullable_with_default: Optional[str] = "hello"

    # -------------------------
    # Nested model (important!)
    # -------------------------

    class InnerModel(BaseModel):
        inner_int: Annotated[int, Field(gt=10)]
        inner_str: str
        inner_optional: Optional[float]

    nested_model: InnerModel
    nested_model_list: List[InnerModel]

    # -------------------------
    # Edge cases for generators
    # -------------------------

    constrained_large_int: Annotated[int, Field(ge=10_000, le=1_000_000)]
    constrained_small_float: Annotated[float, Field(ge=0.0001, le=0.001)]

    empty_allowed_list: Annotated[List[str], Field(min_length=0, max_length=3)]
