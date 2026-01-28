# from pyfake.generators.primivites import generate_int
# from pyfake.core.context import Context

# context = Context(seed=42)

# x = generate_int(context=context)
# print(x)

from pyfake import Pyfake

# from pydantic import BaseModel
from tests.models import StressTestModel
from tests.field_schema import Model


# x = Pyfake.from_schema(StressTestModel, num=1)
x = Pyfake.from_schema(Model, num=1)
print(x)
