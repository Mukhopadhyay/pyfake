from pyfake import Pyfake
from pydantic import BaseModel


class Model(BaseModel):
    thing1: int


def test_numeric():
    d = Pyfake(Model)
    assert True
