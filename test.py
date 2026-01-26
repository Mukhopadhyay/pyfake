# from pyfake.generators.primivites import generate_int
# from pyfake.core.context import Context

# context = Context(seed=42)

# x = generate_int(context=context)
# print(x)

from pyfake import Pyfake
from pydantic import BaseModel
from tests.models import StressTestModel


class Model(BaseModel):
    integer_basic: int


x = Pyfake.from_schema(StressTestModel, num=1)
print(x)
