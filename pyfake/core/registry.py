"""
Resolves the datatypes and forms the generator mapping
"""

from pyfake.generators import primivites


class GeneratorRegistry:
    """
    1. Resolves the type to generator function mapping
    2. Generates data using the resolved generator functions
    """

    def __init__(self):
        self.__generators = {"integer": primivites.generate_int}

    def resolve(self, type_: str):
        pass

    def generate(self):
        pass
