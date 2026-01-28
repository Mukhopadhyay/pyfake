"""
Resolves the datatypes and forms the generator mapping
"""

from pyfake.generators import primivites
from pyfake.schemas import ModelPropertySchema, ResolvedSchema, ResolverArgs
from pyfake.exceptions import GeneratorNotFound

from typing import List, Dict
from collections.abc import Callable


class GeneratorRegistry:
    """
    1. Resolves the type to generator function mapping
    2. Generates data using the resolved generator functions
    """

    def __init__(self):
        self.__generators: Dict[str, Callable] = {
            "integer": primivites.generate_int,
            "null": primivites.generate_none,
        }

    def __resolve_type(self, schema: ModelPropertySchema) -> List[str]:
        """
        input: The model property schema
        output: All possible types and their respective params

        e.g.,

        > a: int | None = None
        >> ['integer', 'none']
        """
        print("1. Resolving type")
        possible_types: List[ResolvedSchema] = []

        if schema.anyOf:
            # Multiple possible values
            for type_ in schema.anyOf:
                possible_types.append(
                    ResolvedSchema(
                        type=type_.type,
                        args=ResolverArgs(ge=type_.minimum, le=type_.maximum),
                    )
                )
        elif schema.type:
            # Scalar type
            possible_types.append(schema.type)

        print("Resolved types:", possible_types)

        return possible_types

    def generate(self, schema: ModelPropertySchema):
        # 1. Resolve the type
        possible_types = self.__resolve_type(schema)

        # generator_func = self.__generators.get(schema.type)
        # if not generator_func:
        #     raise GeneratorNotFound(type_=schema.type)

        # __resolved_schema = ResolvedSchema(
        #     generator_func=generator_func,
        #     args={},
        # )

        # return __resolved_schema.generator_func(**__resolved_schema.args.model_dump())
