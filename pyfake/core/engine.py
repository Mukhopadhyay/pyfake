from collections.abc import Callable, Mapping
from typing import Any

from pydantic import BaseModel

from pyfake.core.context import Context
from pyfake.core.registry import GeneratorRegistry


class Engine:
    """

    Responsible for:
    1. Iterating over the schema properties
    2. Controllin the nunber of samples (items to generate)
    3. Controlling the output format (dict, list, pydantic model, etc)
    """

    def __init__(
        self,
        context: Context | None = None,
        generators: Mapping[Any, Callable[..., Any]] | None = None,
    ):
        self.context = context
        self.registry = GeneratorRegistry(context=self.context, generators=generators)

    def generate(self, schema: type[BaseModel]) -> dict[str, Any]:
        # The registry resolves each field once per model and reuses it for every row
        return self.registry.generate_fields(schema)
