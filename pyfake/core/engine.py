import random
from pydantic import BaseModel
from typing import Optional, Type, Dict, Any, List
from pyfake.parsers.pydantic_parser import PydanticParser
from pyfake.core.types import SupportedFieldType


class Pyfake:

    def __init__(self, model: Type[BaseModel]):
        self.model: Type[BaseModel] = model

    def __choose(self, options: List[str]) -> str:
        return random.choice(options)

    def __generate_value(self, types: List[str]) -> Any:
        selected_type = self.__choose(types)
        if selected_type not in SupportedFieldType.__args__:
            raise ValueError(f"Unsupported type: {selected_type}")

        if selected_type == "integer":
            return random.randint(0, 100)
        elif selected_type == "null":
            return None

    def generate(self, num: Optional[int] = 1) -> Dict[str, Any]:
        parser = PydanticParser(self.model)
        fields = parser.parse()

        data = []
        for _ in range(num):
            item = {}
            for field in fields:
                item[field["name"]] = self.__generate_value(field["types"])
            data.append(item)
        return data
