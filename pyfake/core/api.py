import json
from collections.abc import Callable, Mapping
from typing import Any, TypeVar, cast

from pydantic import BaseModel

from pyfake.core.context import Context
from pyfake.core.engine import Engine
from pyfake.core.registry import _check_registration

T = TypeVar("T", bound=BaseModel)


class Pyfake:
    def __init__(
        self,
        schema: type[BaseModel],
        seed: int | None = None,
        context: Context | None = None,
        *,
        generators: Mapping[Any, Callable[..., Any]] | None = None,
    ):
        self.schema = schema
        self.context = context or Context(seed=seed)
        self.engine = Engine(self.context, generators=generators)

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
        """
        Generate `num` instances. `num=1` (or None) returns a single instance,
        any other number returns a list (empty for `num=0`).
        """
        if num is None:
            num = 1
        if num < 0:
            raise ValueError(f"num must be zero or more, got {num}")

        # by_name: fields with an alias are generated under their field name
        instances = [
            self.schema.model_validate(self.engine.generate(self.schema), by_name=True)
            for _ in range(num)
        ]
        results: list[BaseModel | dict[str, Any]]
        if as_dict:
            results = [instance.model_dump() for instance in instances]
        else:
            results = list(instances)

        return results[0] if num == 1 else results


class Fake:
    def __init__(self, seed: int | None = None):
        self._seed = seed
        # A seeded Fake keeps one random stream across calls, so successive calls return
        # different rows while the whole sequence stays reproducible
        self._context = Context(seed=seed) if seed is not None else None
        # Generators registered on this instance only
        self._generators: dict[Any, Callable[..., Any]] = {}

    def register(self, type_: Any, fn: Callable[..., Any]) -> None:
        """
        Register `fn` as the generator for `type_` on this instance only.

        `fn` is called as `fn(ctx, **constraints)`: `ctx` is a `GeneratorContext` and
        `constraints` holds the field's constraints that are set (e.g. `min_length`, `ge`).
        Registering a type again replaces its generator, and built-in types can be overridden.
        Takes precedence over generators registered with `pyfake.register()`.
        """
        _check_registration(type_, fn)
        self._generators[type_] = fn

    def __call__(
        self,
        schema: type[T],
        num: int = 1,
        *,
        as_dict: bool | None = True,
        seed: int | None = None,
    ) -> BaseModel | dict[str, Any] | list[BaseModel | dict[str, Any]]:
        # An explicit per-call seed always starts a fresh stream
        if seed is not None:
            context = Context(seed=seed)
        else:
            context = self._context or Context()

        return Pyfake(schema, context=context, generators=self._generators).generate(
            num, as_dict=as_dict
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
        # The new instance starts with a copy of this instance's registered generators
        seeded = Fake(seed=seed)
        seeded._generators = dict(self._generators)
        return seeded
