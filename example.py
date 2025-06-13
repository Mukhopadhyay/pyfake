from dummy import Dummy
from pydantic import BaseModel


class Model(BaseModel):
    value: int

dummy = Dummy(Model)
x = dummy.generate(10)

print(x)
