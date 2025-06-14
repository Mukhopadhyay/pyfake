from pydantic import BaseModel
from typing import Type, Optional
from typing import List, Any


class ModelSchema:
    name: str
    types: List[str]
    default: Optional[Any] = None


class PydanticParser:
    """
    A parser class for Pydantic models that extracts fields
    & their types.
    """

    def __init__(self, model: Type[BaseModel]):
        self.__model = model

    def parse(self) -> List[ModelSchema]:
        """
        Returns a dictionary with field and essential attributes
        to generate random data.
        """
        properties = self.__model.model_json_schema().get("properties")
        schema = []

        for field, value in properties.items():
            default_value = value.get("default")

            possible_types = value.get("anyOf", value.get("type"))
            if isinstance(possible_types, list):
                possible_types = [_["type"] for _ in possible_types]
            else:
                possible_types = [
                    possible_types,
                ]

            schema.append(
                {"name": field, "types": possible_types, "default": default_value}
            )

        return schema
