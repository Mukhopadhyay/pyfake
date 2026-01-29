import warnings

warnings.filterwarnings("ignore")
from pyfake import Pyfake

# from tests.models import StressTestModel

from pydantic import BaseModel
from pydantic import BaseModel, Field
from typing import Annotated, Optional, Union


class StressTestModel(BaseModel):
    integer_basic: int
    integer_optional: Optional[int]
    integer_with_bounds: Annotated[int, Field(ge=1, le=100)]
    integer_with_multiple_annotations: Union[
        Annotated[int, Field(ge=1, le=100)], Annotated[int, Field(ge=200, le=300)]
    ]
    integer_with_multiple_annotations: Union[
        Annotated[int, Field(ge=1, le=100, default=21)],
        Annotated[int, Field(ge=200, le=300, default=42)],
    ]
    integer_optional_2_defaults: Optional[
        Annotated[int, Field(ge=1, le=100, default=21)]
    ] = 42
    integer_optional_3_defaults: Union[
        Annotated[int, Field(ge=1, le=10, default=5)],
        Annotated[int, Field(ge=20, le=30, default=29)],
    ] = 27
    integer_optional_default: Optional[int] = 42


class StressTestStringModel(BaseModel):
    string_basic: str
    string_optional: Optional[str]
    string_with_bounds: Annotated[str, Field(min_length=1, max_length=100)]
    string_with_multiple_annotations: Union[
        Annotated[str, Field(min_length=1, max_length=5)],
        Annotated[str, Field(min_length=10, max_length=15)],
    ]
    string_optional_default: Optional[
        Annotated[str, Field(min_length=1, max_length=10, default="abc")]
    ] = "xyz"
    string_with_length_default: Annotated[
        str, Field(min_length=3, max_length=3, default="abc")
    ] = "def"
    string_with_examples: Annotated[
        str, Field(examples=["example1", "example2", "example3"])
    ]


x = Pyfake.from_schema(StressTestStringModel, num=1, seed=1)
print(x)
