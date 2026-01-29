import pytest

from pyfake.core.registry import GeneratorRegistry
from pyfake.core.context import Context
from pyfake.schemas import ModelPropertySchema, AnyOfSchema
from pyfake.exceptions import GeneratorNotFound


def test_generator_not_found_raises_if_anyof():
    ctx = Context(seed=123)
    registry = GeneratorRegistry(context=ctx)

    schema = ModelPropertySchema(
        anyOf=[
            AnyOfSchema(type="unmapped_type"),
        ]
    )

    with pytest.raises(GeneratorNotFound) as excinfo:
        registry.generate(name="field", schema=schema, required_attrs=[])

    assert "No generator registered for type unmapped_type" in str(excinfo.value)


def test_generator_not_found_raises_if_scalar():
    ctx = Context(seed=123)
    registry = GeneratorRegistry(context=ctx)

    schema = ModelPropertySchema(type="unmapped_type")

    with pytest.raises(GeneratorNotFound) as excinfo:
        registry.generate(name="field", schema=schema, required_attrs=[])

    assert "No generator registered for type unmapped_type" in str(excinfo.value)
