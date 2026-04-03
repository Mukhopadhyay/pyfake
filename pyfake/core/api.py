import json
from pydantic import BaseModel
from pyfake.core.engine import Engine
from pyfake.core.context import Context
from typing import Optional, Dict, List, Any, Union


class Pyfake:

    def __init__(self, schema, seed: Optional[int] = None):
        self.schema = schema
        self.context = Context(seed=seed)
        self.engine = Engine(self.context)

    @classmethod
    def from_schema(cls, schema, num=1, seed: Optional[int] = None, as_dict: Optional[bool] = True):
        return cls(schema, seed).generate(num, as_dict=as_dict)

    def generate(
        self, num: Optional[int] = 1, as_dict: Optional[bool] = True
    ) -> Union[Union[BaseModel, Dict[str, Any]], List[Union[BaseModel, Dict[str, Any]]]]:
        if not num:
            num = 1

        if num > 1:
            instances = [self.schema(**self.engine.generate(self.schema)) for _ in range(num)]
            if as_dict:
                return [instance.model_dump() for instance in instances]
            return instances
        else:
            instance = self.schema(**self.engine.generate(self.schema))
            if as_dict:
                return instance.model_dump()
            return instance


class Fake:

    def __init__(self, seed: Optional[int] = None):
        self._seed = seed

    def __call__(
        self,
        schema,
        num: int = 1,
        *,
        as_dict: Optional[bool] = True,
        seed: Optional[int] = None,
    ):
        return Pyfake.from_schema(
            schema=schema,
            num=num,
            seed=seed if seed is not None else self._seed,
            as_dict=as_dict,
        )

    def dict(self, schema, num: int = 1, seed: Optional[int] = None):
        return self(schema=schema, num=num, as_dict=True, seed=seed)

    def model(self, schema, num: int = 1, seed: Optional[int] = None):
        return self(schema=schema, num=num, as_dict=False, seed=seed)

    def seed(self, seed: int):
        return Fake(seed=seed)
