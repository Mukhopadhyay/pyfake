from pyfake import Pyfake
from pydantic import BaseModel
from typing import Optional
from pprint import pprint


class Model(BaseModel):
    integer: int
    optional_integer: Optional[int]
    optional_integer_default_none: Optional[int] = None
    optional_integer_default_42: Optional[int] = 42
    floating_point: float
    optional_floating_point: Optional[float]
    optional_floating_point_default_none: Optional[float] = None
    optional_floating_point_default_3_14: Optional[float] = 3.14

pyf = Pyfake(Model)
data = pyf.generate(num=10)

pprint(data)