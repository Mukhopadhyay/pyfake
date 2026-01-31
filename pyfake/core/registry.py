"""
Resolves the datatypes and forms the generator mapping
"""

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

from typing import List, Dict, Any, Optional, Union
from collections.abc import Callable
from pydantic.fields import FieldInfo
import random


class GeneratorRegistry:
    """
    Responsible for:
    1. Resolving possible types based on FieldInfo
    2. Resolving FieldInfo
    3. Generating value based on the resolved type and FieldInfo
    """

    def __init__(self, context: Context = None):
        self._generators: Dict[str, Union[Callable, Dict[str, Callable]]] = {
            "integer": primitives.generate_int,
            "null": primitives.generate_none,
<<<<<<< HEAD
            "string": primitives.generate_str,
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
=======
            "string": {
                "string": primitives.generate_str,
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
            },
>>>>>>> 8e989d7 (Adding generators for date, datetime & time)
            "number": primitives.generate_float,
        }
        self.__context = context

    def generate(self, attr: FieldInfo):
        schema = Resolver(attr).resolve()["schema"]
        return self._generate(schema)

    def _generate(self, schema):
        t = schema["type"]
        args = schema.get("generator_args")

        # ---------------------
        # Default shortcut
        # ---------------------
        if args and args.default is not None:
            return args.default

        # ---------------------
        # Union
        # ---------------------
        if t == "union":
            variants = schema["variants"]

            if schema.get("nullable") and random.random() < 0.2:
                return None

            variant = random.choice(variants)
            return self._generate(variant)

        # ---------------------
        # Literal
        # ---------------------
        if t == "literal":
            return random.choice(schema["values"])

        # ---------------------
        # Enum
        # ---------------------
        if t == "enum":
            return random.choice(schema["values"])

        # ---------------------
        # List / Set
        # ---------------------
        if t in (list, set):
            length = random.randint(args.min_length or 1, args.max_length or 5)

            items = [self._generate(schema["items"]) for _ in range(length)]

            return items if t is list else set(items)

        # ---------------------
        # Tuple
        # ---------------------
        if t is tuple:

            if schema["mode"] == "variable":
                length = random.randint(args.min_length or 1, args.max_length or 5)

                return tuple(self._generate(schema["items"]) for _ in range(length))

            return tuple(self._generate(i) for i in schema["items"])

        # ---------------------
        # Dict
        # ---------------------
        if t is dict:
            length = random.randint(args.min_length or 1, args.max_length or 5)

            return {
                self._generate(schema["keys"]): self._generate(schema["values"])
                for _ in range(length)
            }

        # ---------------------
        # Nested Model
        # ---------------------
        if t == "model":
            model_cls = schema["model"]

            data = {
                name: self._generate(field_schema)
                for name, field_schema in schema["fields"].items()
            }

            return model_cls(**data)

        # ---------------------
        # Primitive Types
        # ---------------------
        if t is int:
            low = args.ge if args.ge is not None else 0
            high = args.le if args.le is not None else 100
            return random.randint(low, high)

        if t is float:
            low = args.ge if args.ge is not None else 0
            high = args.le if args.le is not None else 100
            return random.uniform(low, high)

        if t is str:
            length = random.randint(args.min_length or 3, args.max_length or 10)
            return "".join(random.choices("abcdefghijklmnopqrstuvwxyz", k=length))

        if t is bool:
            return random.choice([True, False])

        # fallback
        return None
