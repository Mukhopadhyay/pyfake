from pyfake.core.context import Context
from pydantic import BaseModel
from typing import Optional


class Engine:
    """
    Uses the generator registry to generate data based on the schema
    """

    def __init__(self, context: Optional[Context] = None):
        self.context = context

    def generate(self, schema: BaseModel):
        print(schema.model_json_schema())
