import pytest
from pyfake.core.registry import GeneratorRegistry
from pyfake.core.context import Context
from pyfake.exceptions import GeneratorNotFound
from pyfake.schemas import GeneratorArgs
from collections.abc import Callable
from typing import Annotated
from pydantic import BaseModel, Field


@pytest.mark.pyfake
@pytest.mark.registry
class TestPyfakeRegistry:
    def test_generators_registered(self):
        registry = GeneratorRegistry(context=Context())

        for key, value in registry._generators.items():
            assert isinstance(key, str)
            assert isinstance(value, (dict, Callable))

            if isinstance(value, dict):
                for format_key, format_value in value.items():
                    assert isinstance(format_key, str)
                    assert isinstance(format_value, Callable)

    def test_generate_from_field_info(self):
        class M(BaseModel):
            x: Annotated[int, Field(ge=5, le=6)]

        registry = GeneratorRegistry(context=Context(seed=0))
        assert registry.generate(M.model_fields["x"]) in (5, 6)

    def test_unhashable_type_raises_generator_not_found(self):
        registry = GeneratorRegistry(context=Context(seed=0))
        with pytest.raises(GeneratorNotFound):
            registry._generate({"type": ["not", "a", "type"], "generator_args": GeneratorArgs()})

    def test_subclass_of_supported_type(self):
        class Name(str):
            pass

        registry = GeneratorRegistry(context=Context(seed=0))
        assert isinstance(registry._generate({"type": Name, "generator_args": GeneratorArgs()}), str)

    def test_unknown_non_type_raises_generator_not_found(self):
        registry = GeneratorRegistry(context=Context(seed=0))
        with pytest.raises(GeneratorNotFound):
            registry._generate({"type": "mystery", "generator_args": GeneratorArgs()})
