import json
from typing import Any, TypeVar, cast

from pydantic import BaseModel

from pyfake.core.context import Context
from pyfake.core.engine import Engine

T = TypeVar("T", bound=BaseModel)


class Pyfake:
    def __init__(self, schema: type[BaseModel], seed: int | None = None):
        self.schema = schema
        self.context = Context(seed=seed)
        self.engine = Engine(self.context)

    @classmethod
    def from_schema(
        cls,
        schema: type[T],
        num: int = 1,
        seed: int | None = None,
        as_dict: bool | None = True,
    ) -> BaseModel | dict[str, Any] | list[BaseModel | dict[str, Any]]:
        return cls(schema, seed).generate(num, as_dict=as_dict)

    def generate(
        self, num: int | None = 1, as_dict: bool | None = True
    ) -> BaseModel | dict[str, Any] | list[BaseModel | dict[str, Any]]:
        if not num:
            num = 1

        if num > 1:
            instances = [
                self.schema(**self.engine.generate(self.schema)) for _ in range(num)
            ]
            results: list[BaseModel | dict[str, Any]]
            if as_dict:
                results = [instance.model_dump() for instance in instances]
            else:
                results = list(instances)
            return results
        else:
            instance = self.schema(**self.engine.generate(self.schema))
            if as_dict:
                return instance.model_dump()
            return instance


class Fake:
    def __init__(self, seed: int | None = None):
        self._seed = seed

    def __call__(
        self,
        schema: type[T],
        num: int = 1,
        *,
        as_dict: bool | None = True,
        seed: int | None = None,
    ) -> BaseModel | dict[str, Any] | list[BaseModel | dict[str, Any]]:
        return Pyfake.from_schema(
            schema=schema,
            num=num,
            seed=seed if seed is not None else self._seed,
            as_dict=as_dict,
        )

    def dict(
        self, schema: type[T], num: int = 1, seed: int | None = None
    ) -> dict[str, Any] | list[dict[str, Any]]:
        return cast(
            "dict[str, Any] | list[dict[str, Any]]",
            self(schema=schema, num=num, as_dict=True, seed=seed),
        )

    def model(
        self, schema: type[T], num: int = 1, seed: int | None = None
    ) -> BaseModel | list[BaseModel]:
        return cast(
            "BaseModel | list[BaseModel]",
            self(schema=schema, num=num, as_dict=False, seed=seed),
        )

    def json(self, schema: type[T], num: int = 1, seed: int | None = None) -> str:
        data = self(schema=schema, num=num, as_dict=True, seed=seed)
        return json.dumps(data, indent=4, default=str)

    def seed(self, seed: int) -> "Fake":
        return Fake(seed=seed)
