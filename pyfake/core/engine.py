from pyfake.core.context import Context
from pyfake.core.registry import GeneratorRegistry

from pydantic import BaseModel
from typing import Optional, Dict, Any


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

        _data = {}

        for prop, attr in schema.model_fields.items():
            _data[prop] = self.registry.generate(attr)

        return _data
