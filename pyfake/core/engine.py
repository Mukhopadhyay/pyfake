import random
from pydantic import BaseModel
from typing import Optional, Type, Dict, Any, List, Tuple, Literal
from pyfake.parsers.pydantic_parser import PydanticParser
from pyfake.core.types import SupportedFieldType


class Pyfake:

    def __init__(self, model: Type[BaseModel]):
        self.model: Type[BaseModel] = model

    def __choose(
        self, options: List[str], default: Optional[Any] = None
    ) -> Tuple[str, Literal["TYPE", "VALUE"]]:
        """
        Returns a random choice and the type of the choice.
        """
        choices = [{"value": option, "type": "TYPE"} for option in options]
        if default is not None:
            choices.append({"value": default, "type": "VALUE"})

        choice = random.choice(choices)
        return choice["value"], choice["type"]

    def __generate_value(self, types: List[str], default: Optional[Any] = None) -> Any:
        choice_value, choice_type = self.__choose(types, default=default)
        if choice_type == "TYPE" and choice_value not in SupportedFieldType.__args__:
            raise ValueError(f"Unsupported type: {choice_value}")

        if choice_type == "VALUE":
            return choice_value

        if choice_value == "integer":
            return random.randint(0, 100)
        elif choice_value == "null":
            return None

    def generate(self, num: Optional[int] = 1) -> Dict[str, Any]:
        parser = PydanticParser(self.model)
        fields = parser.parse()

        data = []
        for _ in range(num):
            item = {}
            for field in fields:
                item[field["name"]] = self.__generate_value(
                    field["types"], field["default"]
                )
            data.append(item)
        return data
