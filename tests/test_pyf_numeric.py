from pyfake import Pyfake
from pydantic import BaseModel, ValidationError
from typing import Optional
from rich import print


class Model(BaseModel):
    integer: int
    optional_integer: Optional[int]
    optional_integer_default_none: Optional[int] = None
    optional_integer_default_42: Optional[int] = 42
    floating_point: float
    optional_floating_point: Optional[float]
    optional_floating_point_default_none: Optional[float] = None
    optional_floating_point_default_3_14: Optional[float] = 3.14


def test_numeric():
    pyfake = Pyfake(Model)
    result = pyfake.generate(10)
    print(result)

    assert isinstance(result, list)
    assert len(result) == 10
    for item in result:
        try:
            Model(**item)
        except ValidationError:
            assert False, f"Validation error for item: {item}"
