import annotated_types
import collections
import collections.abc
import types
from pydantic import BaseModel
from pydantic.fields import FieldInfo
from pydantic.types import UuidVersion
from pydantic_core import PydanticUndefinedType
from typing import Annotated, Any, Union, Literal, get_args, get_origin
from enum import Enum

from pyfake.schemas import GeneratorArgs

# Abstract and specialised containers are generated as the concrete type pydantic accepts for them
_LIST_ORIGINS = (
    list,
    collections.deque,
    collections.abc.Sequence,
    collections.abc.MutableSequence,
    collections.abc.Iterable,
)
_SET_ORIGINS = (set, collections.abc.Set, collections.abc.MutableSet)
_DICT_ORIGINS = (
    dict,
    collections.OrderedDict,
    collections.defaultdict,
    collections.abc.Mapping,
    collections.abc.MutableMapping,
)
_BARE_CONTAINERS = (
    _LIST_ORIGINS
    + _SET_ORIGINS
    + _DICT_ORIGINS
    + (frozenset, tuple, collections.Counter)
)


class Resolver:
    def __init__(self, field_info: FieldInfo):
        self.field_info = field_info

    @staticmethod
    def __parse(field_info: FieldInfo):

        generator_args = GeneratorArgs()
        # Default value
        if field_info.default is not None and not isinstance(
            field_info.default, PydanticUndefinedType
        ):
            generator_args.default = field_info.default
        # Examples
        if field_info.examples:
            generator_args.examples = field_info.examples
        # Format / Timezone (a callable json_schema_extra only edits the JSON schema, so it's skipped)
        if isinstance(field_info.json_schema_extra, dict):
            generator_args.format = field_info.json_schema_extra.get("format")
            generator_args.timezone = field_info.json_schema_extra.get("timezone")

        Resolver.__apply_metadata(generator_args, field_info.metadata)
        return generator_args

    @staticmethod
    def __flatten(metadata):
        """
        Yield the individual constraints in a metadata list. Grouped metadata such as
        `conint(...)`, `constr(...)`, `Interval(...)` and `StringConstraints(...)` is
        expanded, and the `None` placeholders that pydantic leaves for unset options are skipped.
        """
        for meta in metadata:
            if meta is None:
                continue
            if isinstance(meta, annotated_types.GroupedMetadata):
                yield from Resolver.__flatten(meta)
            else:
                yield meta

    @staticmethod
    def __apply_metadata(generator_args: GeneratorArgs, metadata):
        for meta in Resolver.__flatten(metadata):
            if isinstance(meta, annotated_types.Ge):
                generator_args.ge = meta.ge
            if isinstance(meta, annotated_types.Le):
                generator_args.le = meta.le
            if isinstance(meta, annotated_types.Lt):
                generator_args.lt = meta.lt
            if isinstance(meta, annotated_types.Gt):
                generator_args.gt = meta.gt
            if isinstance(meta, annotated_types.MultipleOf):
                generator_args.multiple_of = meta.multiple_of
            if isinstance(meta, annotated_types.MinLen):
                generator_args.min_length = meta.min_length
            if isinstance(meta, annotated_types.MaxLen):
                generator_args.max_length = meta.max_length
            if isinstance(meta, UuidVersion):
                generator_args.format = f"uuid{meta.uuid_version}"
            if meta.__class__.__name__ == "_PydanticGeneralMetadata":
                if getattr(meta, "pattern", None) is not None:
                    generator_args.pattern = meta.pattern
                if getattr(meta, "decimal_places", None) is not None:
                    generator_args.decimal_places = meta.decimal_places
                if getattr(meta, "max_digits", None) is not None:
                    generator_args.max_digits = meta.max_digits

    @staticmethod
    def __merge(schema, root_args):

        # Union → push constraints to variants (but not default)
        if schema.get("type") == "union":
            for variant in schema["variants"]:
                if "generator_args" not in variant:
                    variant["generator_args"] = GeneratorArgs()

                local = variant["generator_args"]

                for k, v in root_args.__dict__.items():
                    if k == "default" or v is None:
                        continue
                    setattr(local, k, v)

            return schema

        # Normal node
        if "generator_args" not in schema:
            schema["generator_args"] = GeneratorArgs()

        local = schema["generator_args"]

        for k, v in root_args.__dict__.items():
            if v is not None:
                setattr(local, k, v)

        return schema

    def resolve(self):
        annotation = self.field_info.annotation

        def _resolve(tp, inherited_args=None):
            origin = get_origin(tp)
            generator_args = inherited_args or GeneratorArgs()

            # Bare `list`, `dict`, ... behave like `list[Any]`, `dict[Any, Any]`, ...
            if origin is None and tp in _BARE_CONTAINERS:
                origin = tp

            # Annotated[T, Field(...)]
            if origin is Annotated:
                base, *meta = get_args(tp)

                local_args = GeneratorArgs()

                for m in meta:
                    if isinstance(m, FieldInfo):
                        parsed = self.__parse(m)
                        # Defaults in Annotated metadata have no effect
                        # (consistent with pydantic behavior)
                        parsed.default = None

                        for k, v in parsed.__dict__.items():
                            if v is not None:
                                setattr(local_args, k, v)
                    else:
                        # Raw constraints, e.g. `conint(gt=0)` or `Annotated[int, Gt(0)]`
                        self.__apply_metadata(local_args, [m])

                merged = GeneratorArgs()

                # inherit previous constraints
                if inherited_args:  # pragma: no cover
                    for k, v in inherited_args.__dict__.items():
                        setattr(merged, k, v)

                # apply annotated constraints
                for k, v in local_args.__dict__.items():
                    if v is not None:
                        setattr(merged, k, v)

                return _resolve(base, merged)

            # Union / Optional
            if origin is Union or origin is types.UnionType:
                args = get_args(tp)

                variants = []
                nullable = False

                for arg in args:
                    if arg is type(None):
                        nullable = True
                        continue

                    variants.append(_resolve(arg))

                return {
                    "type": "union",
                    "variants": variants,
                    "nullable": nullable,
                }

            # List / Set / FrozenSet (and their abstract counterparts, e.g. Sequence)
            if origin in _LIST_ORIGINS or origin in _SET_ORIGINS or origin is frozenset:
                args = get_args(tp)

                if origin is frozenset:
                    container = frozenset
                elif origin in _SET_ORIGINS:
                    container = set
                else:
                    container = list

                return {
                    "type": container,
                    "items": _resolve(args[0] if args else Any),
                    "generator_args": generator_args,
                }

            # Tuple
            if origin is tuple:
                args = get_args(tp)

                # Tuple[int, ...] (or a bare tuple)
                if not args or (len(args) == 2 and args[1] is Ellipsis):
                    return {
                        "type": tuple,
                        "mode": "variable",
                        "items": _resolve(args[0] if args else Any),
                        "generator_args": generator_args,
                    }

                # Tuple[int, str]
                return {
                    "type": tuple,
                    "mode": "fixed",
                    "items": [_resolve(a) for a in args],
                    "generator_args": generator_args,
                }

            # Dict (Counter[K] maps keys to int counts)
            if origin in _DICT_ORIGINS or origin is collections.Counter:
                args = get_args(tp)

                if origin is collections.Counter:
                    k, v = (args[0] if args else Any), int
                else:
                    k, v = args if args else (Any, Any)

                return {
                    "type": dict,
                    "keys": _resolve(k),
                    "values": _resolve(v),
                    "generator_args": generator_args,
                }

            # Nested Pydantic model. Its fields are resolved lazily by the registry,
            # so self-referencing models don't recurse forever here.
            if isinstance(tp, type) and issubclass(tp, BaseModel):
                return {
                    "type": "model",
                    "model": tp,
                    "generator_args": generator_args,
                }

            # Literals
            if origin is Literal:
                args = get_args(tp)

                return {
                    "type": "literal",
                    "values": args,
                    "generator_args": generator_args,
                }

            # Enums
            if isinstance(tp, type) and issubclass(tp, Enum):
                return {
                    "type": "enum",
                    "enum_class": tp,
                    "values": [e.value for e in tp],
                    "generator_args": generator_args,
                }

            # Primitive
            return {
                "type": tp,
                "generator_args": generator_args,
            }

        schema = _resolve(annotation)

        # root FieldInfo metadata still applies
        root_args = self.__parse(self.field_info)

        schema = self.__merge(schema, root_args)

        return {
            "schema": schema,
        }
