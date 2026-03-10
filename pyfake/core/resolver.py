import annotated_types
from pydantic import BaseModel
from pydantic.fields import FieldInfo
from pydantic_core import PydanticUndefinedType
from typing import Annotated, Union, get_args, get_origin

from pyfake.schemas import GeneratorArgs


class Resolver:
    def __init__(self, field_info: FieldInfo):
        self.field_info = field_info

    @staticmethod
    def __parse(field_info: FieldInfo):
        generator_args = GeneratorArgs()
        if not field_info.metadata:
            return generator_args

        # Default value
        if field_info.default is not None and not isinstance(
            field_info.default, PydanticUndefinedType
        ):
            generator_args.default = field_info.default
        # Examples
        if field_info.examples:
            generator_args.examples = field_info.examples
        # Format
        if field_info.json_schema_extra and "format" in field_info.json_schema_extra:
            generator_args.format = field_info.json_schema_extra["format"]

        for meta in field_info.metadata:
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
            if meta.__class__.__name__ == "_PydanticGeneralMetadata":
                if meta.pattern is not None:
                    generator_args.pattern = meta.pattern
                if hasattr(meta, "decimal_places") and meta.decimal_places is not None:
                    generator_args.decimal_places = meta.decimal_places
        return generator_args

    @staticmethod
    def __merge(schema, root_args):
        """
        Attach root generator args to the schema node itself.
        Do NOT propagate to children (containers keep their own constraints).
        """

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

            # Annotated[T, Field(...)]
            if origin is Annotated:
                base, *meta = get_args(tp)

                local_args = GeneratorArgs()

                for m in meta:
                    if isinstance(m, FieldInfo):
                        parsed = self.__parse(m)

                        for k, v in parsed.__dict__.items():
                            if v is not None:
                                setattr(local_args, k, v)

                # return _resolve(base, local_args)
                merged = GeneratorArgs()

                # inherit previous constraints
                if inherited_args:
                    for k, v in inherited_args.__dict__.items():
                        setattr(merged, k, v)

                # apply annotated constraints
                for k, v in local_args.__dict__.items():
                    if v is not None:
                        setattr(merged, k, v)

                return _resolve(base, merged)

            # Union / Optional
            if origin is Union:
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

            # List / Set
            if origin in (list, set):
                args = get_args(tp)

                return {
                    "type": origin,
                    "items": _resolve(args[0]) if args else None,
                    "generator_args": generator_args,
                }

            # Tuple
            if origin is tuple:
                args = get_args(tp)

                # Tuple[int, ...]
                if len(args) == 2 and args[1] is Ellipsis:
                    return {
                        "type": tuple,
                        "mode": "variable",
                        "items": _resolve(args[0]),
                        "generator_args": generator_args,
                    }

                # Tuple[int, str]
                return {
                    "type": tuple,
                    "mode": "fixed",
                    "items": [_resolve(a) for a in args],
                    "generator_args": generator_args,
                }

            # Dict
            if origin is dict:
                k, v = get_args(tp)

                return {
                    "type": dict,
                    "keys": _resolve(k),
                    "values": _resolve(v),
                    "generator_args": generator_args,
                }

            # Nested Pydantic model
            if isinstance(tp, type) and issubclass(tp, BaseModel):
                return {
                    "type": "model",
                    "model": tp,
                    "fields": {
                        k: Resolver(v).resolve()["schema"]
                        for k, v in tp.model_fields.items()
                    },
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
            # "generator_args": root_args,
        }
