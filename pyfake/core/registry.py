"""
Resolves the datatypes and forms the generator mapping
"""

import datetime as dt_mod
import ipaddress
import uuid as uuid_mod
from collections.abc import Callable
from dataclasses import fields
from decimal import Decimal
from functools import partial
from typing import Any

import pydantic
from pydantic import BaseModel
from pydantic.fields import FieldInfo
from pydantic.networks import UrlConstraints

from pyfake.core.context import Context
from pyfake.core.resolver import Resolver
from pyfake.exceptions import GeneratorNotFound, InvalidConstraints
from pyfake.generators import datetime, network, primitives, uuid
from pyfake.generators.bounds import check_range, resolve_bounds
from pyfake.schemas import GeneratorArgs

# Arguments that the registry uses itself rather than passing to generators
_REGISTRY_ARGS = {"default", "examples", "format"}

# Self-referencing models stop growing once a model appears this many times on the current path
MAX_DEPTH = 3
# Beyond MAX_DEPTH, only fields that can't be left empty keep going. Past this many
# extra levels the model can't be generated with finite depth.
_RECURSION_LIMIT = MAX_DEPTH + 10


class GeneratorRegistry:
    """
    Responsible for:
    1. Resolving possible types based on FieldInfo
    2. Resolving FieldInfo
    3. Generating value based on the resolved type and FieldInfo
    """

    def __init__(self, context: Context | None = None):
        # Keys match the JSON schema `format` names where one exists, so
        # `json_schema_extra={"format": ...}` can pick any of these generators
        self._generators: dict[str, Callable[..., Any]] = {
            "integer": primitives.generate_int,
            "null": primitives.generate_none,
            "string": primitives.generate_str,
            "bool": primitives.generate_bool,
            "binary": primitives.generate_bytes,
            "any": primitives.generate_any,
            "uuid": uuid.generate_uuid4,
            "uuid1": uuid.generate_uuid1,
            "uuid3": uuid.generate_uuid3,
            "uuid4": uuid.generate_uuid4,
            "uuid5": uuid.generate_uuid5,
            "uuid6": uuid.generate_uuid6,
            "uuid7": uuid.generate_uuid7,
            "uuid8": uuid.generate_uuid8,
            "date": datetime.generate_date,
            "past-date": datetime.generate_past_date,
            "future-date": datetime.generate_future_date,
            "date-time": datetime.generate_datetime,
            "aware-date-time": datetime.generate_aware_datetime,
            "past-date-time": datetime.generate_past_datetime,
            "future-date-time": datetime.generate_future_datetime,
            "time": datetime.generate_time,
            "duration": datetime.generate_timedelta,
            "number": primitives.generate_float,
            "decimal": primitives.generate_decimal,
            "email": network.generate_email,
            "name-email": network.generate_name_email,
            "uri": network.generate_url,
            "ipv4": partial(network.generate_ip_address, version=4),
            "ipv6": partial(network.generate_ip_address, version=6),
            "ipvanyaddress": network.generate_ip_address,
            "ipv4network": partial(network.generate_ip_network, version=4),
            "ipv6network": partial(network.generate_ip_network, version=6),
            "ipvanynetwork": network.generate_ip_network,
            "ipv4interface": partial(network.generate_ip_interface, version=4),
            "ipv6interface": partial(network.generate_ip_interface, version=6),
            "ipvanyinterface": network.generate_ip_interface,
        }
        self._type_map: dict[Any, str] = {
            int: "integer",
            float: "number",
            Decimal: "decimal",
            str: "string",
            bool: "bool",
            bytes: "binary",
            type(None): "null",
            Any: "any",
            object: "any",
            uuid_mod.UUID: "uuid",
            dt_mod.datetime: "date-time",
            dt_mod.date: "date",
            dt_mod.time: "time",
            dt_mod.timedelta: "duration",
            pydantic.PastDate: "past-date",
            pydantic.FutureDate: "future-date",
            pydantic.AwareDatetime: "aware-date-time",
            pydantic.NaiveDatetime: "date-time",
            pydantic.PastDatetime: "past-date-time",
            pydantic.FutureDatetime: "future-date-time",
            pydantic.SecretStr: "string",
            pydantic.SecretBytes: "binary",
            pydantic.EmailStr: "email",
            pydantic.NameEmail: "name-email",
            ipaddress.IPv4Address: "ipv4",
            ipaddress.IPv6Address: "ipv6",
            pydantic.IPvAnyAddress: "ipvanyaddress",
            ipaddress.IPv4Network: "ipv4network",
            ipaddress.IPv6Network: "ipv6network",
            pydantic.IPvAnyNetwork: "ipvanynetwork",
            ipaddress.IPv4Interface: "ipv4interface",
            ipaddress.IPv6Interface: "ipv6interface",
            pydantic.IPvAnyInterface: "ipvanyinterface",
        }
        self.__context = context or Context()
        self._model_fields: dict[type, dict[str, dict]] = {}
        # Models currently being generated, outermost first
        self._model_stack: list[type] = []

    def generate(self, attr: FieldInfo, path: str = "") -> object:
        schema = Resolver(attr).resolve()["schema"]
        return self._generate(schema, path)

    def generate_fields(
        self, model: type[BaseModel], path: str | None = None
    ) -> dict[str, Any]:
        """
        Generate a value for every field of a pydantic model, keyed by field name
        """
        path = path or model.__name__

        if self._model_stack.count(model) >= _RECURSION_LIMIT:
            raise InvalidConstraints(
                f"'{model.__name__}' refers to itself through fields that can't be left empty (at '{path}'), "
                "so it can't be generated. Make the self-reference Optional or a list, or give it a default."
            )

        if model not in self._model_fields:
            # Like pydantic does on first use, resolve forward references to models defined later
            if not model.__pydantic_complete__:
                model.model_rebuild()

            self._model_fields[model] = {
                name: Resolver(field_info).resolve()["schema"]
                for name, field_info in model.model_fields.items()
            }

        self._model_stack.append(model)
        try:
            return {
                name: self._generate(schema, f"{path}.{name}")
                for name, schema in self._model_fields[model].items()
            }
        finally:
            self._model_stack.pop()

    def _generate(self, schema: dict[str, Any], path: str = "") -> object:
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

            # Deep inside a self-referencing model, prefer variants that stop the recursion
            if self._is_deep():
                shallow = [v for v in variants if not self._too_deep(v)]
                if not shallow and schema.get("nullable"):
                    return None
                variants = shallow or variants

            if schema.get("nullable") and rng.random() < 0.2:
                return None

            variant = rng.choice(variants)
            return self._generate(variant, path)

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
        # List / Set / FrozenSet
        # ---------------------
        if t is list:
            length = self._length(args, [schema["items"]])
            return [self._generate(schema["items"], f"{path}[]") for _ in range(length)]

        if t in (set, frozenset):
            length = self._length(args, [schema["items"]])
            items = self._unique(schema["items"], length, args.min_length, f"{path}[]")
            return t(items)

        # ---------------------
        # Tuple
        # ---------------------
        if t is tuple:
            if schema["mode"] == "variable":
                length = self._length(args, [schema["items"]])

                return tuple(
                    self._generate(schema["items"], f"{path}[]") for _ in range(length)
                )

            return tuple(
                self._generate(item, f"{path}[{i}]")
                for i, item in enumerate(schema["items"])
            )

        # ---------------------
        # Dict
        # ---------------------
        if t is dict:
            length = self._length(args, [schema["keys"], schema["values"]])
            keys = self._unique(schema["keys"], length, args.min_length, f"{path}[key]")

            return {
                key: self._generate(schema["values"], f"{path}[{key!r}]")
                for key in keys
            }

        # ---------------------
        # Nested Model
        # ---------------------
        if t == "model":
            model_cls = schema["model"]

            data = self.generate_fields(model_cls, path)

            # by_name: fields with an alias are generated under their field name
            return model_cls.model_validate(data, by_name=True)

        # ---------------------
        # Format-based dispatch
        # (uuid, date, date-time, time, etc.)
        # ---------------------
        if args.format and args.format in self._generators:
            return self._call(self._generators[args.format], args)

        # ---------------------
        # URL / DSN types (HttpUrl, PostgresDsn, ...) carry their allowed schemes
        # ---------------------
        url_constraints = getattr(t, "_constraints", None)
        if isinstance(url_constraints, UrlConstraints):
            return self._call(network.generate_url, args, constraints=url_constraints)

        # ---------------------
        # Primitive Types
        # ---------------------
        type_key = self._type_key(t)
        if type_key and type_key in self._generators:
            return self._call(self._generators[type_key], args)

        raise GeneratorNotFound(t, path)

    def _call(self, gen_func: Callable, args: GeneratorArgs, **extra):
        gen_kwargs = {
            f.name: getattr(args, f.name)
            for f in fields(args)
            if f.name not in _REGISTRY_ARGS
        }
        return gen_func(context=self.__context, **gen_kwargs, **extra)

    def _type_key(self, t):
        try:
            if t in self._type_map:
                return self._type_map[t]
        except TypeError:  # unhashable annotation
            return None

        # Subclasses of supported types, e.g. pydantic's ByteSize (an int)
        if isinstance(t, type):
            for base in t.__mro__[1:-1]:
                if base in self._type_map:
                    return self._type_map[base]
        return None

    def _length(self, args: GeneratorArgs, item_schemas) -> int:
        """
        Pick a container length within min_length/max_length (1 to 5 by default)
        """
        lower, upper = resolve_bounds(args.min_length, args.max_length, 1, 5, floor=0)
        check_range(lower, upper, "length")

        # Deep inside a self-referencing model, add as few nested items as the constraints allow
        if self._is_deep() and any(self._too_deep(s) for s in item_schemas):
            return args.min_length or 0

        return self.__context.random.randint(lower, upper)

    def _unique(self, schema, length: int, min_length, path: str) -> list:
        """
        Generate `length` distinct values, or at least `min_length` of them
        """
        domain = self._domain_size(schema)
        minimum = min_length or 0
        if domain is not None:
            if domain < minimum:
                raise InvalidConstraints(
                    f"'{path}' needs {minimum} distinct values, but only {domain} exist."
                )
            length = min(length, domain)

        # dict keys keep the generation order, so seeded output is stable
        values = {}
        attempts = length * 10 + 10
        while len(values) < length and attempts:
            values.setdefault(self._generate(schema, path), None)
            attempts -= 1

        if len(values) < minimum:
            raise InvalidConstraints(
                f"Could only generate {len(values)} distinct values for '{path}', but at least {minimum} are needed."
            )
        return list(values)

    def _domain_size(self, schema):
        """
        The number of distinct values a schema can produce, when it is small and known
        """
        t = schema["type"]
        if t in ("literal", "enum"):
            return len(set(schema["values"]))
        if t is bool:
            return 2
        if t == "union":
            sizes = [self._domain_size(v) for v in schema["variants"]]
            if None in sizes:
                return None
            return sum(sizes) + (1 if schema.get("nullable") else 0)
        return None

    def _is_deep(self) -> bool:
        # A model can only appear MAX_DEPTH times on a path that is at least that long
        return len(self._model_stack) >= MAX_DEPTH

    def _too_deep(self, schema) -> bool:
        """
        True when generating `schema` would enter a model that already appears MAX_DEPTH
        times on the current path
        """
        t = schema["type"]
        if t == "model":
            return self._model_stack.count(schema["model"]) >= MAX_DEPTH
        if t == "union":
            children = schema["variants"]
        elif t in (list, set, frozenset):
            children = [schema["items"]]
        elif t is tuple:
            children = (
                schema["items"] if schema["mode"] == "fixed" else [schema["items"]]
            )
        elif t is dict:
            children = [schema["keys"], schema["values"]]
        else:
            return False
        return any(self._too_deep(child) for child in children)
