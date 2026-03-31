from pyfake.core.engine import Engine
from pyfake.core.context import Context
from typing import Optional, Dict, List, Any, Union
from pydantic import BaseModel


class Pyfake:

    def __init__(self, schema, seed: Optional[int] = None):
        self.schema = schema
        self.context = Context(seed=seed)
        self.engine = Engine(self.context)

    @classmethod
    def from_schema(
        cls, schema, num=1, seed: Optional[int] = None, as_dict: Optional[bool] = True
    ):
        return cls(schema, seed).generate(num, as_dict=as_dict)

    def generate(
        self, num: Optional[int] = 1, as_dict: Optional[bool] = True
    ) -> Union[
        Union[BaseModel, Dict[str, Any]], List[Union[BaseModel, Dict[str, Any]]]
    ]:
        if not num:
            num = 1

        if num > 1:
            instances = [
                self.schema(**self.engine.generate(self.schema)) for _ in range(num)
            ]
            if as_dict:
                return [instance.model_dump() for instance in instances]
            return instances
        else:
            instance = self.schema(**self.engine.generate(self.schema))
            if as_dict:
                return instance.model_dump()
            return instance
