"""
Resolves the datatypes and forms the generator mapping
"""

from pyfake.generators import primivites
from pyfake.schemas.models import ModelPropertySchema, ResolvedSchema
from pyfake.exceptions import GeneratorNotFound


class GeneratorRegistry:
    """
    1. Resolves the type to generator function mapping
    2. Generates data using the resolved generator functions
    """

    def __init__(self):
        self.__generators = {"integer": primivites.generate_int}

    def __resolve(self, type_: str):
        """
        Internal function for resolving type to generator function mapping
        """
        pass

    def generate(self, schema: ModelPropertySchema):
        """
        1. Resolves the generator function
        2. Generate the data with valid args
        """
        generator_func = self.__generators.get(schema.type)
        if not generator_func:
            raise GeneratorNotFound(type_=schema.type)

        __resolved_schema = ResolvedSchema(
            generator_func=generator_func,
            args={},
        )

        return __resolved_schema.generator_func(**__resolved_schema.args.model_dump())
