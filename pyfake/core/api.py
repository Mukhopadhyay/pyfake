import json
from pydantic import BaseModel
from pyfake.core.engine import Engine
from pyfake.core.context import Context
from typing import Optional, Dict, List, Any, Union, Type, TypeVar

T = TypeVar("T", bound=BaseModel)


class Pyfake:

    def __init__(self, schema: Type[T], seed: Optional[int] = None, context: Optional[Context] = None):
        self.schema = schema
        self.context = context or Context(seed=seed)
        self.engine = Engine(self.context)

    @classmethod
    def from_schema(cls, schema: Type[T], num=1, seed: Optional[int] = None, as_dict: Optional[bool] = True):
        return cls(schema, seed).generate(num, as_dict=as_dict)

    def generate(
        self, num: Optional[int] = 1, as_dict: Optional[bool] = True
    ) -> Union[Union[BaseModel, Dict[str, Any]], List[Union[BaseModel, Dict[str, Any]]]]:
        """
        Generate `num` instances. `num=1` (or None) returns a single instance,
        any other number returns a list (empty for `num=0`).
        """
        if num is None:
            num = 1
        if num < 0:
            raise ValueError(f"num must be zero or more, got {num}")

        # by_name: fields with an alias are generated under their field name
        instances = [self.schema.model_validate(self.engine.generate(self.schema), by_name=True) for _ in range(num)]
        results = [instance.model_dump() for instance in instances] if as_dict else instances

        return results[0] if num == 1 else results


class Fake:

    def __init__(self, seed: Optional[int] = None):
        self._seed = seed
        # A seeded Fake keeps one random stream across calls, so successive calls return
        # different rows while the whole sequence stays reproducible
        self._context = Context(seed=seed) if seed is not None else None

    def __call__(
        self,
        schema: Type[T],
        num: int = 1,
        *,
        as_dict: Optional[bool] = True,
        seed: Optional[int] = None,
    ):
        # An explicit per-call seed always starts a fresh stream
        if seed is not None:
            context = Context(seed=seed)
        else:
            context = self._context or Context()

        return Pyfake(schema, context=context).generate(num, as_dict=as_dict)

    def dict(self, schema: Type[T], num: int = 1, seed: Optional[int] = None):
        return self(schema=schema, num=num, as_dict=True, seed=seed)

    def model(self, schema: Type[T], num: int = 1, seed: Optional[int] = None):
        return self(schema=schema, num=num, as_dict=False, seed=seed)

    def json(self, schema: Type[T], num: int = 1, seed: Optional[int] = None):
        data = self(schema=schema, num=num, as_dict=True, seed=seed)
        return json.dumps(data, indent=4, default=str)

    def seed(self, seed: int):
        return Fake(seed=seed)
