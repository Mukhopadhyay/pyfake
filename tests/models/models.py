from typing import Annotated

from pydantic import BaseModel, Field

# Field docs:
# https://docs.pydantic.dev/latest/api/fields/#pydantic.fields.Field


class StressTestModel(BaseModel):
    # -------------------------
    # Basic primitives
    # -------------------------

    integer_basic: int
    integer_optional: int | None
    integer_with_bounds: Annotated[int, Field(ge=1, le=100)]
    integer_with_multiple_annotations: (
        Annotated[int, Field(ge=1, le=100)] | Annotated[int, Field(ge=200, le=300)]
    )
    integer_optional_2_defaults: (
        Annotated[int, Field(ge=1, le=100, default=21)] | None
    ) = 42
    integer_optional_3_defaults: (
        Annotated[int, Field(ge=1, le=10, default=5)]
        | Annotated[int, Field(ge=20, le=30, default=29)]
    ) = 27
    integer_optional_default: int | None = 42

    # float_basic: float
    # float_with_bounds: Annotated[float, Field(gt=0.0, lt=1.0)]

    # boolean_basic: bool
    # boolean_default: bool = True

    # string_basic: str
    # string_with_length: Annotated[str, Field(min_length=5, max_length=20)]
    # string_regex: Annotated[str, Field(pattern=r"^[a-z]{3}[0-9]{2}$")]
    # string_default: str = "default_value"

    # # -------------------------
    # # Common real-world types
    # # -------------------------

    # uuid_value: UUID
    # uuid_default: UUID = Field(default_factory=uuid4)

    # email: EmailStr
    # website: HttpUrl

    # # -------------------------
    # # Date & time types
    # # -------------------------

    # datetime_basic: datetime
    # datetime_past: Annotated[datetime, Field(le=datetime.now())]

    # date_basic: date
    # date_future: Annotated[date, Field(gt=date.today())]

    # time_basic: time

    # # -------------------------
    # # Collections
    # # -------------------------

    # int_list: List[int]
    # bounded_list: Annotated[List[int], Field(min_length=1, max_length=5)]

    # nested_list: List[List[str]]

    # string_dict: Dict[str, str]
    # mixed_dict: Dict[str, int]

    # # -------------------------
    # # Optional + nullable combos
    # # -------------------------

    # nullable_string: Optional[str] = None
    # nullable_with_default: Optional[str] = "hello"

    # # -------------------------
    # # Nested model (important!)
    # # -------------------------

    # class InnerModel(BaseModel):
    #     inner_int: Annotated[int, Field(gt=10)]
    #     inner_str: str
    #     inner_optional: Optional[float]

    # nested_model: InnerModel
    # nested_model_list: List[InnerModel]

    # # -------------------------
    # # Edge cases for generators
    # # -------------------------

    # constrained_large_int: Annotated[int, Field(ge=10_000, le=1_000_000)]
    # constrained_small_float: Annotated[float, Field(ge=0.0001, le=0.001)]

    # empty_allowed_list: Annotated[List[str], Field(min_length=0, max_length=3)]


class Model(BaseModel):
    title: str = Field(title="Model Title")
    frozen: str = Field(frozen=True)
    description: str = Field(description="This is a description of the model.")
    alias: str = Field(alias="model_alias")
    examples: str = Field(examples=["example1", 1])
    examples_annotated: Annotated[str | int, Field(examples=["example2", 2])]
    gt: int = Field(gt=10)
    lt: int = Field(lt=100)
    ge: int = Field(ge=5)
    le: int = Field(le=200)
    default: int = Field(default=42)
    multi_default: Annotated[int | str, Field(default=99)]
    pattern: str = Field(pattern=r"^[a-zA-Z0-9_]+$")
    allow_inf_nan: float = Field(allow_inf_nan=False)
    multiple_of: int = Field(multiple_of=3)
    decimal_places: float = Field(decimal_places=2)
    min_length: str = Field(min_length=3)
    max_length: str = Field(max_length=50)
