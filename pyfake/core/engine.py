from pyfake.core.context import Context
from pyfake.core.registry import GeneratorRegistry

from pydantic import BaseModel
from typing import Optional, Dict, Any

from pyfake import schemas


class Engine:
    """
    Uses the generator registry to generate data based on the schema
    """

    def __init__(self, context: Optional[Context] = None):
        self.context = context
        self.registry = GeneratorRegistry()

    def generate(self, schema: BaseModel) -> dict[str, Any]:
        from rich import print

        print(schema.model_json_schema())

        model_property: Dict[str, schemas.ModelPropertySchema] = (
            schema.model_json_schema()["properties"]
        )

        # This is going to be populated after the for loop
        _data = {}

        for key, value in model_property.items():
            """
            1. Resolve the type of the generator function
            2. Generate the value
            """
            schema = schemas.ModelPropertySchema(**value)
            _data[key] = self.registry.generate(schema)

        return _data
