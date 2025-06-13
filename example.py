from pyfake import Pyfake
from pydantic import BaseModel
from rich import print

from typing import Optional


class Model(BaseModel):
    integer: int
    optional_integer: Optional[int]
    optional_integer_default_none: Optional[int] = None


pyfake = Pyfake(Model)
x = pyfake.generate(10)

print(x)
