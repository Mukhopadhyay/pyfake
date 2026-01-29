from pyfake import Pyfake
from tests.models import StressTestModel


x = Pyfake.from_schema(StressTestModel, num=1)
print(x)
