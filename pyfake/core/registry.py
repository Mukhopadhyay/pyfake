"""
Resolves the datatypes and forms the generator mapping
"""

import uuid as uuid_mod
import datetime as dt_mod

from pyfake.generators import primitives, uuid, datetime
from pyfake.core.context import Context
from pyfake.schemas import (
    ModelPropertySchema,
    ResolvedSchema,
    GeneratorArgs,
    FieldSchema,
)
from pyfake.exceptions import GeneratorNotFound
from pyfake.core.resolver import Resolver

from typing import List, Dict
from collections.abc import Callable
from pydantic.fields import FieldInfo


class GeneratorRegistry:
    """
    Responsible for:
    1. Resolving possible types based on FieldInfo
    2. Resolving FieldInfo
    3. Generating value based on the resolved type and FieldInfo
    """

    def __init__(self, context: Context = None):
        self._generators: Dict[str, Callable] = {
            "integer": primitives.generate_int,
            "null": primitives.generate_none,
            "string": primitives.generate_str,
            "bool": primitives.generate_bool,
            "uuid": uuid.generate_uuid4,
            "uuid1": uuid.generate_uuid1,
            "uuid3": uuid.generate_uuid3,
            "uuid4": uuid.generate_uuid4,
            "uuid5": uuid.generate_uuid5,
            "uuid6": uuid.generate_uuid6,
            "uuid7": uuid.generate_uuid7,
            "uuid8": uuid.generate_uuid8,
            "date": datetime.generate_date,
            "date-time": datetime.generate_datetime,
            "time": datetime.generate_time,
            "number": primitives.generate_float,
        }
        self._type_map: Dict[type, str] = {
            int: "integer",
            float: "number",
            str: "string",
            bool: "bool",
            uuid_mod.UUID: "uuid",
            dt_mod.datetime: "date-time",
            dt_mod.date: "date",
            dt_mod.time: "time",
        }
        self.__context = context or Context()

    def generate(self, attr: FieldInfo):
        schema = Resolver(attr).resolve()["schema"]
        return self._generate(schema)

    def _generate(self, schema):
        t = schema["type"]
        args = schema.get("generator_args") or GeneratorArgs()

        rng = self.__context.random

        # ---------------------
        # Default shortcut
        # ---------------------
        if args.default is not None:
            return args.default

        # ---------------------
        # Union
        # ---------------------
        if t == "union":
            variants = schema["variants"]

            if schema.get("nullable") and rng.random() < 0.2:
                return None

            variant = rng.choice(variants)
            return self._generate(variant)

        # ---------------------
        # Literal
        # ---------------------
        if t == "literal":
            return rng.choice(schema["values"])

        # ---------------------
        # Enum
        # ---------------------
        if t == "enum":
            return rng.choice(schema["values"])

        # ---------------------
        # List / Set
        # ---------------------
        if t in (list, set):
            length = rng.randint(args.min_length or 1, args.max_length or 5)

            items = [self._generate(schema["items"]) for _ in range(length)]

            return items if t is list else set(items)

        # ---------------------
        # Tuple
        # ---------------------
        if t is tuple:

            if schema["mode"] == "variable":
                length = rng.randint(args.min_length or 1, args.max_length or 5)

                return tuple(self._generate(schema["items"]) for _ in range(length))

            return tuple(self._generate(i) for i in schema["items"])

        # ---------------------
        # Dict
        # ---------------------
        if t is dict:
            length = rng.randint(args.min_length or 1, args.max_length or 5)

            return {self._generate(schema["keys"]): self._generate(schema["values"]) for _ in range(length)}

        # ---------------------
        # Nested Model
        # ---------------------
        if t == "model":
            model_cls = schema["model"]

            data = {name: self._generate(field_schema) for name, field_schema in schema["fields"].items()}

            return model_cls(**data)

        # ---------------------
        # Format-based dispatch
        # (uuid, date, date-time, time, etc.)
        # ---------------------
        if args.format and args.format in self._generators:
            gen_func = self._generators[args.format]
            gen_kwargs = args.model_dump(exclude={"default", "examples", "format"})
            return gen_func(context=self.__context, **gen_kwargs)

        # ---------------------
        # Primitive Types
        # ---------------------
        type_key = self._type_map.get(t)
        if type_key and type_key in self._generators:
            gen_func = self._generators[type_key]
            gen_kwargs = args.model_dump(exclude={"default", "examples", "format"})
            return gen_func(context=self.__context, **gen_kwargs)

        # fallback
        return None
