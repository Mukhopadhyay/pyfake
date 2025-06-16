import random
from pydantic import BaseModel
import types
from typing import Optional, Type, Dict, Any, List, Tuple, Literal
from pyfake.parsers.pydantic_parser import PydanticParser
from pyfake.core.types import SupportedFieldType
from pyfake.generators import number

# Module map
_dtype_to_mod = {"integer": number, "number": number}


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

    def __resolve_module(self, type_name: str) -> Optional[types.ModuleType]:
        """
        Based on the type name, resolve the corresponding module.
        """
        return _dtype_to_mod.get(type_name)

    def __generate_value(self, types: List[str], default: Optional[Any] = None) -> Any:
        choice_value, choice_type = self.__choose(types, default=default)

        if choice_type == "TYPE" and choice_value not in SupportedFieldType.__args__:
            raise ValueError(f"Unsupported type: {choice_value}")

        if choice_type == "VALUE":
            return choice_value

        # Identify the module
        module = self.__resolve_module(choice_value)
        if not module:
            return

        func = getattr(module, choice_value)
        return func()

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
