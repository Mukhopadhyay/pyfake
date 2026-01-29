"""
Resolves the datatypes and forms the generator mapping
"""

from pyfake.generators import primitives
from pyfake.core.context import Context
from pyfake.schemas import ModelPropertySchema, ResolvedSchema, GeneratorArgs
from pyfake.exceptions import GeneratorNotFound

from typing import List, Dict, Any
from collections.abc import Callable


from rich import print


class GeneratorRegistry:
    """
    1. Resolves the type to generator function mapping
    2. Generates data using the resolved generator functions
    """

    def __init__(self, context: Context = None):
        self.__generators: Dict[str, Callable] = {
            "integer": primitives.generate_int,
            "null": primitives.generate_none,
            "string": primitives.generate_str,
            "number": primitives.generate_float,
        }
        self.__context = context

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

                __generator_func = self.__generators.get(current_type)
                if not __generator_func:
                    raise GeneratorNotFound(type_=current_type)

                possible_types.append(
                    ResolvedSchema(
                        type=current_type,
                        generator_func=__generator_func,
                        args=GeneratorArgs(
                            lt=type_.exclusiveMaximum,
                            gt=type_.exclusiveMinimum,
                            le=type_.maximum,
                            ge=type_.minimum,
                            default=type_.default,
                            pattern=type_.examples,
                            multiple_of=type_.multipleOf,
                            decimal_places=type_.multipleOf,
                            min_length=type_.minLength,
                            max_length=type_.maxLength,
                            examples=type_.examples,
                            is_optional=name not in required_attrs,
                        ),
                    )
                )
        elif schema.type:
            # Scalar type
            # Resolve the generator function
            __generator_func = self.__generators.get(schema.type)
            if not __generator_func:
                raise GeneratorNotFound(type_=schema.type)

            possible_types.append(
                ResolvedSchema(
                    type=schema.type,
                    generator_func=__generator_func,
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
                        is_optional=name not in required_attrs,
                    ),
                )
            )

        # print("Resolved types:", possible_types)
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

        if selected_type.args.is_optional:
            possible_values.append(None)

        # Generated value
        generated_value = selected_type.generator_func(
            **selected_type.args.model_dump(exclude_none=True), context=self.__context
        )
        possible_values.append(generated_value)

        return self.__context.random.choice(possible_values)
