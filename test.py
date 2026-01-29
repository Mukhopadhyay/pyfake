from pyfake import Pyfake

from tests.models import StressTestModel
from tests.field_schema import Model


x = Pyfake.from_schema(StressTestModel, num=1)
# x = Pyfake.from_schema(Model, num=1, seed=None)
print(x)
