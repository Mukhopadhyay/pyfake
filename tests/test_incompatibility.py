from pyfake import Pyfake
from pydantic import BaseModel


class Model(BaseModel):
    string: str


def test_imcompatible_types():
    pyfake = Pyfake(Model)
    # Assert error
    try:
        _ = pyfake.generate(10)
    except ValueError as e:
        assert str(e) == "Unsupported type: string"
    else:
        assert False, "Expected ValueError for incompatible types not raised"
