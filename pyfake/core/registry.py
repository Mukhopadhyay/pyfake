"""
Resolves the datatypes and forms the generator mapping
"""

from pyfake.generators import primitives, uuid
from pyfake.core.context import Context
from pyfake.schemas import (
    ModelPropertySchema,
    ResolvedSchema,
    GeneratorArgs,
    FieldSchema,
)
from pyfake.exceptions import GeneratorNotFound

from typing import List, Dict, Any, Optional, Union
from collections.abc import Callable


class GeneratorRegistry:
    """
    1. Resolves the type to generator function mapping
    2. Generates data using the resolved generator functions
    """

    def __init__(self, context: Context = None):
        self._generators: Dict[str, Union[Callable, Dict[str, Callable]]] = {
            "integer": primitives.generate_int,
            "null": primitives.generate_none,
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
            },
            "number": primitives.generate_float,
        }
        self.__context = context

    def __resolve_generator(
        self, type_: str, format: Optional[str] = None
    ) -> Union[Callable, None]:
        _generator_result: Union[Callable, Dict[str, Callable]] = self._generators.get(
            type_
        )
        if isinstance(_generator_result, dict):
            if format is None:
                _func = _generator_result.get(type_)
                if not _func:
                    raise GeneratorNotFound(type_=type_)
                return _func
            else:
                _func = _generator_result.get(format)
                if not _func:
                    raise GeneratorNotFound(type_=f"{type_} with format {format}")
                return _func
        elif isinstance(_generator_result, Callable):
            _func = _generator_result
            return _func
        else:
            raise GeneratorNotFound(type_=type_)

    def __get_resolved_schema(
        self,
        type_: str,
        schema: FieldSchema,
    ) -> ResolvedSchema:

        # Figure out the generator function
        generator_func = self.__resolve_generator(type_=type_, format=schema.format)

        return ResolvedSchema(
            type=type_,
            generator_func=generator_func,
            args=GeneratorArgs(
                lt=schema.exclusiveMaximum,
                gt=schema.exclusiveMinimum,
                le=schema.maximum,
                ge=schema.minimum,
                default=schema.default,
                pattern=schema.pattern,
                multiple_of=schema.multipleOf,
                decimal_places=schema.multipleOf,
                min_length=schema.minLength,
                max_length=schema.maxLength,
                examples=schema.examples,
                # is_optional=name not in required_attrs,
                format=schema.format,
            ),
        )

    def __resolve_type(
        self, name: str, schema: ModelPropertySchema, required_attrs: List[str]
    ) -> List[ResolvedSchema]:
        """
        input: The model property schema
        output: All possible types and their respective params

        e.g.,

        > a: int | None = None
        >> ['integer', 'none']
        """
        possible_types: List[ResolvedSchema] = []

        if schema.anyOf:
            # Multiple possible values
            for type_ in schema.anyOf:

                current_type = type_.type or schema.type
                possible_types.append(
                    self.__get_resolved_schema(
                        type_=current_type,
                        schema=type_,
                    )
                )
        else:
            possible_types.append(
                self.__get_resolved_schema(
                    type_=schema.type,
                    schema=schema,
                )
            )

        return possible_types

    def generate(
        self, name: str, schema: ModelPropertySchema, required_attrs: List[str]
    ) -> Any:
        # 1. Resolve the type
        possible_types = self.__resolve_type(
            name=name, schema=schema, required_attrs=required_attrs
        )

        # 2. If multiple possible values pick the type first
        selected_type = self.__context.random.choice(possible_types)

        # 3. Look for defaults & examples
        # The value for this attribute is gonna be one of
        # S = {
        #     default, -- If default is not None
        #     example1, example2, ... -- If examples are present
        #     generated_value
        #     None -- If the field is optional
        # }
        possible_values = []
        if selected_type.args.default is not None:
            possible_values.append(selected_type.args.default)

        if selected_type.args.examples:
            possible_values.extend(selected_type.args.examples)

        # Generated value
        generated_value = selected_type.generator_func(
            **selected_type.args.model_dump(exclude_none=True), context=self.__context
        )
        possible_values.append(generated_value)

        return self.__context.random.choice(possible_values)
