"""
Integration and unit tests for complex types: Literal, Enum, List, Set, Tuple, Dict,
nested models, nullable union, registry fallback, and resolver edge cases.
"""

import pytest
import uuid as uuid_mod
from decimal import Decimal
from enum import Enum
from typing import Annotated, Dict, List, Literal, Optional, Set, Tuple

import pydantic
from pydantic import BaseModel, Field

from pyfake import Pyfake
from pyfake.core.context import Context
from pyfake.core.registry import GeneratorRegistry
from pyfake.core.resolver import Resolver
from pyfake.schemas import GeneratorArgs


# ---------------------------------------------------------------------------
# Shared fixtures / helpers
# ---------------------------------------------------------------------------


class Color(Enum):
    RED = "red"
    GREEN = "green"
    BLUE = "blue"


# ---------------------------------------------------------------------------
# Literal
# ---------------------------------------------------------------------------


@pytest.mark.pyfake
@pytest.mark.complex
class TestPyfakeLiteralGeneration:

    class LiteralModel(BaseModel):
        status: Literal["active", "inactive", "pending"]
        code: Literal[1, 2, 3]

    @pytest.mark.parametrize("seed", list(range(10)) + [None])
    def test_literal_fields_produce_valid_values(self, seed):
        result = Pyfake(self.LiteralModel, seed=seed).generate()
        assert isinstance(result, dict)
        assert result["status"] in {"active", "inactive", "pending"}
        assert result["code"] in {1, 2, 3}


# ---------------------------------------------------------------------------
# Enum
# ---------------------------------------------------------------------------


@pytest.mark.pyfake
@pytest.mark.complex
class TestPyfakeEnumGeneration:

    class EnumModel(BaseModel):
        color: Color
        optional_color: Optional[Color]

    @pytest.mark.parametrize("seed", list(range(10)) + [None])
    def test_enum_field_produces_valid_value(self, seed):
        result = Pyfake(self.EnumModel, seed=seed).generate()
        assert isinstance(result, dict)
        # pydantic model_dump() in Python mode returns the enum member itself
        assert isinstance(result["color"], Color)
        assert result["optional_color"] is None or isinstance(result["optional_color"], Color)


# ---------------------------------------------------------------------------
# List / Set
# ---------------------------------------------------------------------------


@pytest.mark.pyfake
@pytest.mark.complex
class TestPyfakeCollectionGeneration:

    class CollectionModel(BaseModel):
        int_list: List[int]
        str_set: Set[str]
        nested_list: List[List[int]]

    @pytest.mark.parametrize("seed", list(range(5)) + [None])
    def test_list_field_generates_list_of_correct_type(self, seed):
        result = Pyfake(self.CollectionModel, seed=seed).generate()
        assert isinstance(result, dict)
        assert isinstance(result["int_list"], list)
        assert all(isinstance(i, int) for i in result["int_list"])
        assert len(result["int_list"]) >= 1

    @pytest.mark.parametrize("seed", list(range(5)) + [None])
    def test_set_field_generates_serializable_collection(self, seed):
        result = Pyfake(self.CollectionModel, seed=seed).generate()
        # pydantic serialises Set to list in model_dump()
        assert isinstance(result["str_set"], (list, set))

    def test_nested_list_generates_list_of_lists(self):
        result = Pyfake(self.CollectionModel, seed=1).generate()
        assert isinstance(result["nested_list"], list)
        assert all(isinstance(inner, list) for inner in result["nested_list"])

    def test_set_is_generated_by_registry_directly(self):
        context = Context(seed=0)
        registry = GeneratorRegistry(context=context)
        schema = {
            "type": set,
            "items": {"type": int, "generator_args": GeneratorArgs()},
            "generator_args": GeneratorArgs(),
        }
        result = registry._generate(schema)
        assert isinstance(result, set)

    def test_bounded_list_length(self):
        class BoundedModel(BaseModel):
            items: Annotated[List[int], Field(min_length=2, max_length=4)]

        result = Pyfake(BoundedModel, seed=42).generate()
        assert 2 <= len(result["items"]) <= 4


# ---------------------------------------------------------------------------
# Tuple
# ---------------------------------------------------------------------------


@pytest.mark.pyfake
@pytest.mark.complex
class TestPyfakeTupleGeneration:

    class TupleModel(BaseModel):
        variable_tuple: Tuple[int, ...]
        fixed_tuple: Tuple[int, str]

    @pytest.mark.parametrize("seed", list(range(5)) + [None])
    def test_variable_tuple_generates_sequence(self, seed):
        result = Pyfake(self.TupleModel, seed=seed).generate()
        assert isinstance(result, dict)
        assert isinstance(result["variable_tuple"], (list, tuple))

    @pytest.mark.parametrize("seed", list(range(5)) + [None])
    def test_fixed_tuple_generates_sequence_with_correct_types(self, seed):
        result = Pyfake(self.TupleModel, seed=seed).generate()
        assert isinstance(result["fixed_tuple"], (list, tuple))
        ft = list(result["fixed_tuple"])
        assert isinstance(ft[0], int)
        assert isinstance(ft[1], str)

    def test_variable_tuple_generated_by_registry_directly(self):
        context = Context(seed=0)
        registry = GeneratorRegistry(context=context)
        schema = {
            "type": tuple,
            "mode": "variable",
            "items": {"type": int, "generator_args": GeneratorArgs()},
            "generator_args": GeneratorArgs(),
        }
        result = registry._generate(schema)
        assert isinstance(result, tuple)
        assert all(isinstance(v, int) for v in result)


# ---------------------------------------------------------------------------
# Dict
# ---------------------------------------------------------------------------


@pytest.mark.pyfake
@pytest.mark.complex
class TestPyfakeDictGeneration:

    class DictModel(BaseModel):
        scores: Dict[str, int]
        mapping: Dict[int, float]

    @pytest.mark.parametrize("seed", list(range(5)) + [None])
    def test_dict_field_generates_dict_of_correct_types(self, seed):
        result = Pyfake(self.DictModel, seed=seed).generate()
        assert isinstance(result, dict)
        assert isinstance(result["scores"], dict)
        assert all(isinstance(k, str) for k in result["scores"])
        assert all(isinstance(v, int) for v in result["scores"].values())
        assert len(result["scores"]) >= 1

    def test_dict_generated_by_registry_directly(self):
        context = Context(seed=0)
        registry = GeneratorRegistry(context=context)
        schema = {
            "type": dict,
            "keys": {"type": str, "generator_args": GeneratorArgs()},
            "values": {"type": int, "generator_args": GeneratorArgs()},
            "generator_args": GeneratorArgs(),
        }
        result = registry._generate(schema)
        assert isinstance(result, dict)
        assert all(isinstance(k, str) for k in result)
        assert all(isinstance(v, int) for v in result.values())


# ---------------------------------------------------------------------------
# Nested Model
# ---------------------------------------------------------------------------


@pytest.mark.pyfake
@pytest.mark.complex
class TestPyfakeNestedModelGeneration:

    class Inner(BaseModel):
        x: int
        label: str

    class Outer(BaseModel):
        inner: "TestPyfakeNestedModelGeneration.Inner"
        value: int

    @pytest.mark.parametrize("seed", list(range(5)) + [None])
    def test_nested_model_generates_valid_structure(self, seed):
        class Inner(BaseModel):
            x: int
            label: str

        class Outer(BaseModel):
            inner: Inner
            value: int

        result = Pyfake(Outer, seed=seed).generate()
        assert isinstance(result, dict)
        assert isinstance(result["inner"], dict)
        assert isinstance(result["inner"]["x"], int)
        assert isinstance(result["inner"]["label"], str)
        assert isinstance(result["value"], int)


# ---------------------------------------------------------------------------
# Nullable union (registry line 97)
# ---------------------------------------------------------------------------


@pytest.mark.pyfake
@pytest.mark.complex
class TestNullableUnion:
    """Directly tests the nullable branch in GeneratorRegistry._generate."""

    def test_nullable_union_returns_none_when_rng_triggers(self):
        # random.Random(seed=1).random() == 0.134 < 0.2 → nullable branch fires
        context = Context(seed=1)
        registry = GeneratorRegistry(context=context)
        schema = {
            "type": "union",
            "variants": [{"type": int, "generator_args": GeneratorArgs()}],
            "nullable": True,
        }
        result = registry._generate(schema)
        assert result is None

    def test_nullable_union_returns_value_when_rng_does_not_trigger(self):
        # random.Random(seed=0).random() == 0.844 > 0.2 → variant chosen instead
        context = Context(seed=0)
        registry = GeneratorRegistry(context=context)
        schema = {
            "type": "union",
            "variants": [{"type": int, "generator_args": GeneratorArgs()}],
            "nullable": True,
        }
        result = registry._generate(schema)
        assert isinstance(result, int)

    def test_non_nullable_union_always_returns_value(self):
        context = Context(seed=1)
        registry = GeneratorRegistry(context=context)
        schema = {
            "type": "union",
            "variants": [{"type": int, "generator_args": GeneratorArgs()}],
            "nullable": False,
        }
        result = registry._generate(schema)
        assert isinstance(result, int)


# ---------------------------------------------------------------------------
# Registry fallback (line 164)
# ---------------------------------------------------------------------------


@pytest.mark.pyfake
@pytest.mark.complex
class TestRegistryFallback:
    """Tests the fallback path in GeneratorRegistry._generate for unsupported types."""

    def test_unknown_type_returns_none(self):
        context = Context(seed=0)
        registry = GeneratorRegistry(context=context)
        # bytes is not in _type_map → falls through to `return None`
        schema = {"type": bytes, "generator_args": GeneratorArgs()}
        result = registry._generate(schema)
        assert result is None


# ---------------------------------------------------------------------------
# Resolver edge cases
# ---------------------------------------------------------------------------


@pytest.mark.pyfake
@pytest.mark.complex
class TestResolverEdgeCases:

    def test_json_schema_extra_format_is_parsed(self):
        """Covers resolver.py line 29: json_schema_extra format field."""

        class M(BaseModel):
            x: uuid_mod.UUID = Field(json_schema_extra={"format": "uuid1"})

        fi = M.model_fields["x"]
        result = Resolver(fi).resolve()
        assert result["schema"]["generator_args"].format == "uuid1"

    def test_multiple_of_metadata_is_parsed(self):
        """Covers resolver.py line 44: multiple_of from FieldInfo metadata."""

        class M(BaseModel):
            x: Annotated[int, Field(multiple_of=5)]

        fi = M.model_fields["x"]
        result = Resolver(fi).resolve()
        assert result["schema"]["generator_args"].multiple_of == 5

    def test_decimal_places_metadata_is_parsed(self):
        """Covers resolver.py lines 55-56: decimal_places from FieldInfo metadata."""

        class M(BaseModel):
            x: Annotated[Decimal, Field(decimal_places=2)]

        fi = M.model_fields["x"]
        result = Resolver(fi).resolve()
        assert result["schema"]["generator_args"].decimal_places == 2

    def test_union_merge_propagates_root_constraints_to_variants(self):
        """Covers resolver.py line 90: setattr to propagate outer constraints into union variants."""

        class M(BaseModel):
            x: Optional[int] = Field(ge=0, le=100)

        fi = M.model_fields["x"]
        result = Resolver(fi).resolve()
        schema = result["schema"]
        assert schema["type"] == "union"
        # ge/le should have been pushed to the int variant
        int_variant = next(v for v in schema["variants"] if v["type"] is int)
        assert int_variant["generator_args"].ge == 0
        assert int_variant["generator_args"].le == 100

    def test_annotated_uuid_inside_list_covers_uuid_version_branch(self):
        """Covers resolver.py lines 121->131 and 132: UuidVersion metadata in Annotated inner type."""

        class M(BaseModel):
            ids: List[pydantic.UUID1]

        fi = M.model_fields["ids"]
        result = Resolver(fi).resolve()
        items_schema = result["schema"]["items"]
        # The inner UUID type should have format="uuid1" from UuidVersion metadata
        assert items_schema["generator_args"].format == "uuid1"

    def test_nested_annotated_inherits_outer_constraints(self):
        """Covers resolver.py lines 139-140: inherited_args propagated in nested Annotated resolution."""
        BoundedInt = Annotated[int, Field(ge=1)]

        class M(BaseModel):
            items: List[Annotated[BoundedInt, Field(le=100)]]

        fi = M.model_fields["items"]
        result = Resolver(fi).resolve()
        items_schema = result["schema"]["items"]
        # Both ge=1 (inner) and le=100 (outer annotated) should be present
        assert items_schema["generator_args"].ge == 1
        assert items_schema["generator_args"].le == 100

    def test_pattern_metadata_is_parsed(self):
        """Covers resolver.py line 54: pattern from _PydanticGeneralMetadata, and branch 55->34."""

        class M(BaseModel):
            code: Annotated[str, Field(pattern=r"^[A-Z]{3}$")]

        fi = M.model_fields["code"]
        result = Resolver(fi).resolve()
        assert result["schema"]["generator_args"].pattern == r"^[A-Z]{3}$"
        # decimal_places is None → covers branch 55->34 (False branch of line 55)
        assert result["schema"]["generator_args"].decimal_places is None

    def test_merge_adds_generator_args_to_variant_when_missing(self):
        """Covers resolver.py line 83: __merge adds generator_args to union variant if absent."""
        schema = {
            "type": "union",
            "variants": [{"type": int}],  # no generator_args
            "nullable": False,
        }
        Resolver._Resolver__merge(schema, GeneratorArgs(ge=0))
        assert "generator_args" in schema["variants"][0]

    def test_merge_adds_generator_args_to_normal_node_when_missing(self):
        """Covers resolver.py line 96: __merge adds generator_args to normal schema if absent."""
        schema = {"type": int}  # no generator_args
        Resolver._Resolver__merge(schema, GeneratorArgs())
        assert "generator_args" in schema


# ---------------------------------------------------------------------------
# Pyfake integration for complex types using resolver paths
# ---------------------------------------------------------------------------


@pytest.mark.pyfake
@pytest.mark.complex
class TestPyfakeMultipleOf:

    class MultipleOfModel(BaseModel):
        even: Annotated[int, Field(multiple_of=2, ge=0, le=20)]
        precise: Annotated[Decimal, Field(decimal_places=2)]

    @pytest.mark.parametrize("seed", list(range(5)) + [None])
    def test_multiple_of_int_field(self, seed):
        result = Pyfake(self.MultipleOfModel, seed=seed).generate()
        assert result["even"] % 2 == 0
        assert 0 <= result["even"] <= 20

    @pytest.mark.parametrize("seed", list(range(5)) + [None])
    def test_decimal_places_field(self, seed):
        result = Pyfake(self.MultipleOfModel, seed=seed).generate()
        val = result["precise"]
        quantizer = Decimal(10) ** -2
        assert val == val.quantize(quantizer)


@pytest.mark.pyfake
@pytest.mark.complex
class TestPyfakeJsonSchemaExtraFormat:
    """Covers the json_schema_extra format path in pyfake generation."""

    def test_json_schema_extra_uuid_format_generates_uuid(self):
        class M(BaseModel):
            custom_id: uuid_mod.UUID = Field(json_schema_extra={"format": "uuid4"})

        result = Pyfake(M, seed=0).generate()
        assert isinstance(result, dict)
        # Should have generated a UUID string
        uuid_val = uuid_mod.UUID(str(result["custom_id"]))
        assert uuid_val.version == 4
