from dummy import Dummy
from pydantic import BaseModel


class Model(BaseModel):
    thing1: int

def test_numeric():
    d = Dummy(Model)
    assert True
