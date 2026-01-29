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


x = Pyfake.from_schema(StressTestModel, num=1, seed=1)
print(x)
