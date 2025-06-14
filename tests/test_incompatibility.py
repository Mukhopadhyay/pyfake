from pyfake import Pyfake
from pydantic import BaseModel, ValidationError
from typing import Optional
from rich import print


class Model(BaseModel):
    string: str


def test_imcompatible_types():
    pyfake = Pyfake(Model)
    # Assert error
    try:
        result = pyfake.generate(10)
    except ValueError as e:
        assert str(e) == "Unsupported type: string"
    else:
        assert False, "Expected ValueError for incompatible types not raised"
