from pyfake.core.engine import Engine
from pyfake.core.context import Context
from typing import Optional, Dict, List, Any, Union


class Pyfake:

    def __init__(self, schema, seed: Optional[int] = None):
        self.schema = schema
        self.context = Context(seed=seed)
        self.engine = Engine(self.context)

    @classmethod
    def from_schema(cls, schema, num=1, seed: Optional[int] = None):
        return cls(schema, seed).generate(num)

    def generate(
        self, num: Optional[int] = 1
    ) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        if not num:
            num = 1

        if num > 1:
            return [self.engine.generate(self.schema) for _ in range(num)]
        else:
            return self.engine.generate(self.schema)
