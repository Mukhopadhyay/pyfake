from pyfake.core.engine import Engine
from pyfake.core.context import Context
from typing import Optional


class Pyfake:

    def __init__(self, schema, seed: Optional[int] = None):
        self.schema = schema
        self.context = Context(seed=seed)
        self.engine = Engine(self.context)

    @classmethod
    def from_schema(cls, schema, num=1, seed: Optional[int] = None):
        return cls(schema, seed).generate(num)

    def generate(self, num=1):
        return [self.engine.generate(self.schema) for _ in range(num)]
