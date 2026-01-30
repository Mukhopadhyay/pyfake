import pytest
from pyfake.core.registry import GeneratorRegistry
from pyfake.core.context import Context
from collections.abc import Callable


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
