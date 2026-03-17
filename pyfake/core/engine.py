from pyfake.core.context import Context
from pyfake.core.registry import GeneratorRegistry

from pydantic import BaseModel
from typing import Optional, Dict, Any, List

from pyfake import schemas


class Engine:
    """

    Responsible for:
    1. Iterating over the schema properties
    2. Controllin the nunber of samples (items to generate)
    3. Controlling the output format (dict, list, pydantic model, etc)
    """

    def __init__(self, context: Optional[Context] = None):
        self.context = context
        self.registry = GeneratorRegistry(context=self.context)

    def generate(self, schema: BaseModel) -> Dict[str, Any]:

        # from rich import print

        # print(schema)
        # print(schema.model_json_schema())
        # print(schema.model_fields["date_with_bounds"])

        # model_property: Dict[str, schemas.ModelPropertySchema] = (
        #     schema.model_json_schema()["properties"]
        # )
        # required_attributes: List[str] = schema.model_json_schema()["required"]

        # This is going to be populated after the for loop
        # _data = {}

        # for key, value in model_property.items():
        #     """
        #     1. Resolve the type of the generator function
        #     2. Generate the value
        #     """
        #     schema = schemas.ModelPropertySchema(**value)
        #     _data[key] = self.registry.generate(
        #         name=key, schema=schema, required_attrs=required_attributes
        #     )

        _data = {}

        for prop, attr in schema.model_fields.items():
            _data[prop] = self.registry.generate(attr)

        return _data
