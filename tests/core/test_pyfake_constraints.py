"""
Integration tests for constrained types (conint, constr, StringConstraints, ...), field
aliases, self-referencing models, container lengths and uniqueness.
"""

import re
from datetime import date, datetime
from decimal import Decimal
from typing import (
    Annotated,
    Dict,
    FrozenSet,
    List,
    Literal,
    Optional,
    Set,
    Tuple,
    Union,
)

import pytest
from annotated_types import Gt, Interval, Lt
from pydantic import (
    AliasChoices,
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    condecimal,
    confloat,
    conint,
    conlist,
    constr,
)

from pyfake import Pyfake, fake
from pyfake.exceptions import InvalidConstraints

SEEDS = list(range(20)) + [None]


@pytest.mark.pyfake
@pytest.mark.complex
class TestConstrainedTypes:
    """conint/constr/... wrap their constraints in grouped metadata, which must be unpacked."""

    class ConModel(BaseModel):
        small: conint(gt=0, lt=3)
        word: constr(min_length=2, max_length=4)
        ratio: confloat(ge=1.5, le=1.6)
        price: condecimal(max_digits=5, decimal_places=2)
        upper: Annotated[
            str, StringConstraints(min_length=3, max_length=3, to_upper=True)
        ]
        interval: Annotated[int, Interval(gt=1, lt=5)]
        raw: Annotated[int, Gt(10), Lt(13)]
        smalls: List[conint(gt=0, lt=3)]
        bounded: conlist(int, min_length=2, max_length=3)
        code: constr(pattern=r"^[A-Z]{2}\d{2}$")

    @pytest.mark.parametrize("seed", SEEDS)
    def test_values_respect_constraints(self, seed):
        result = fake(self.ConModel, seed=seed)
        assert 0 < result["small"] < 3
        assert 2 <= len(result["word"]) <= 4
        assert 1.5 <= result["ratio"] <= 1.6
        assert abs(result["price"]) < 1000
        assert len(result["upper"]) == 3
        assert 1 < result["interval"] < 5
        assert 10 < result["raw"] < 13
        assert all(0 < v < 3 for v in result["smalls"])
        assert 2 <= len(result["bounded"]) <= 3
        assert re.fullmatch(r"[A-Z]{2}\d{2}", result["code"])


@pytest.mark.pyfake
@pytest.mark.complex
class TestOneSidedBoundsIntegration:
    class Model(BaseModel):
        big: Annotated[int, Field(ge=500)]
        negative: Annotated[int, Field(le=-5)]
        far_future: Annotated[date, Field(ge=date(2200, 1, 1))]
        long_ago: Annotated[datetime, Field(lt=datetime(1900, 1, 1))]
        price: Annotated[Decimal, Field(gt=1000)]

    @pytest.mark.parametrize("seed", SEEDS)
    def test_model_is_valid(self, seed):
        result = fake(self.Model, seed=seed)
        assert result["big"] >= 500
        assert result["negative"] <= -5
        assert result["far_future"] >= date(2200, 1, 1)
        assert result["long_ago"] < datetime(1900, 1, 1)
        assert result["price"] > 1000


@pytest.mark.pyfake
@pytest.mark.complex
class TestPattern:
    class Model(BaseModel):
        sku: Annotated[str, Field(pattern=r"^[A-Z]{3}-\d{4}$")]
        slug: Annotated[
            str, Field(pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$", max_length=20)
        ]
        codes: List[Annotated[str, Field(pattern=r"^\d{3}$")]]

    @pytest.mark.parametrize("seed", SEEDS)
    def test_pattern_fields_match(self, seed):
        result = fake(self.Model, seed=seed)
        assert re.fullmatch(r"[A-Z]{3}-\d{4}", result["sku"])
        assert len(result["slug"]) <= 20
        assert all(re.fullmatch(r"\d{3}", c) for c in result["codes"])

    def test_impossible_pattern_raises(self):
        class M(BaseModel):
            code: Annotated[str, Field(pattern=r"^[A-Z]{3}$", min_length=5)]

        with pytest.raises(InvalidConstraints):
            fake(M, seed=1)


class AliasedInner(BaseModel):
    user_id: int = Field(alias="userId")


class AliasedOuter(BaseModel):
    model_config = ConfigDict(validate_by_name=False)

    inner: AliasedInner = Field(alias="Inner")
    tags: List[str] = Field(validation_alias=AliasChoices("labels", "tagList"))
    maybe: Optional[int] = Field(alias="Maybe")


@pytest.mark.pyfake
@pytest.mark.complex
class TestAliases:
    @pytest.mark.parametrize("seed", SEEDS)
    def test_aliased_fields_are_generated(self, seed):
        result = fake(AliasedOuter, seed=seed)
        assert isinstance(result["inner"]["user_id"], int)
        assert isinstance(result["tags"], list)

    def test_as_model(self):
        result = fake(AliasedOuter, seed=1, as_dict=False)
        assert isinstance(result.inner, AliasedInner)


class Node(BaseModel):
    value: int
    children: List["Node"]
    parent: Optional["Node"] = None


class Tree(BaseModel):
    left: Optional["Tree"]
    right: Optional["Tree"]
    label: str


class Employee(BaseModel):
    name: str
    manager: Optional["Manager"]


class Manager(BaseModel):
    reports: Dict[str, Employee]


class Graph(BaseModel):
    name: str
    pair: Tuple[Optional["Graph"], int]
    many: Tuple["Graph", ...]
    by_name: Dict[str, "Graph"]


class FrozenNode(BaseModel):
    # Frozen, so instances are hashable and can go in a frozenset
    model_config = ConfigDict(frozen=True)

    name: str
    children: FrozenSet["FrozenNode"]


class Nested(BaseModel):
    # Self-references wrapped in more than one container
    maybe_list: Optional[List["Nested"]]
    pairs: List[Tuple["Nested", int]]
    grouped: Dict[str, List["Nested"]]
    maybe_many: Optional[Tuple["Nested", ...]]
    maybe_items: List[Optional["Nested"]]
    maybe_map: Optional[Dict[str, "Nested"]]
    maybe_frozen: Optional[FrozenSet[int]]
    label: Optional[str]


class Loop(BaseModel):
    again: "Loop"


class NonEmptyLoop(BaseModel):
    items: Annotated[List["NonEmptyLoop"], Field(min_length=1)]


def _depth(node: dict, key: str) -> int:
    children = node.get(key) or []
    if isinstance(children, dict):
        children = [children]
    return 1 + max((_depth(c, key) for c in children), default=0)


@pytest.mark.pyfake
@pytest.mark.complex
class TestSelfReferencingModels:
    @pytest.mark.parametrize("seed", SEEDS)
    def test_list_of_self(self, seed):
        result = fake(Node, seed=seed)
        assert _depth(result, "children") <= 3

    @pytest.mark.parametrize("seed", SEEDS)
    def test_optional_self(self, seed):
        result = fake(Tree, seed=seed, as_dict=False)
        assert isinstance(result, Tree)

    @pytest.mark.parametrize("seed", SEEDS)
    def test_recursion_through_tuples_dicts_and_frozensets(self, seed):
        assert isinstance(fake(Graph, seed=seed, as_dict=False), Graph)
        assert isinstance(fake(FrozenNode, seed=seed, as_dict=False), FrozenNode)

    @pytest.mark.parametrize("seed", SEEDS)
    def test_recursion_through_nested_containers(self, seed):
        assert isinstance(fake(Nested, seed=seed, as_dict=False), Nested)

    @pytest.mark.parametrize("seed", SEEDS)
    def test_mutual_recursion(self, seed):
        result = fake(Employee, seed=seed, as_dict=False)
        assert isinstance(result, Employee)

    def test_required_self_reference_raises(self):
        with pytest.raises(InvalidConstraints, match="Loop"):
            fake(Loop, seed=1)

    def test_non_empty_self_reference_raises(self):
        with pytest.raises(InvalidConstraints, match="NonEmptyLoop"):
            fake(NonEmptyLoop, seed=1)

    def test_deterministic_with_seed(self):
        assert fake(Node, seed=4) == fake(Node, seed=4)


@pytest.mark.pyfake
@pytest.mark.complex
class TestContainerLengths:
    class Model(BaseModel):
        empty_list: Annotated[List[int], Field(min_length=0, max_length=0)]
        maybe_empty: Annotated[List[int], Field(min_length=0, max_length=2)]
        long_list: Annotated[List[int], Field(min_length=10)]
        empty_dict: Annotated[Dict[int, int], Field(max_length=0)]
        empty_tuple: Annotated[Tuple[int, ...], Field(max_length=0)]
        empty_set: Annotated[Set[int], Field(max_length=0)]

    @pytest.mark.parametrize("seed", SEEDS)
    def test_lengths(self, seed):
        result = fake(self.Model, seed=seed)
        assert result["empty_list"] == []
        assert len(result["maybe_empty"]) <= 2
        assert len(result["long_list"]) >= 10
        assert result["empty_dict"] == {}
        assert len(result["empty_tuple"]) == 0
        assert len(result["empty_set"]) == 0

    def test_min_length_zero_can_be_empty(self):
        lengths = {
            len(fake(self.Model, seed=seed)["maybe_empty"]) for seed in range(50)
        }
        assert 0 in lengths


@pytest.mark.pyfake
@pytest.mark.complex
class TestUniqueCollections:
    class Model(BaseModel):
        flags: Annotated[Set[bool], Field(min_length=2)]
        exact: Annotated[Set[int], Field(min_length=5, max_length=5)]
        choices: Annotated[Set[Literal["a", "b", "c"]], Field(min_length=3)]
        keys: Annotated[Dict[bool, int], Field(min_length=2)]
        maybe: Annotated[Set[Optional[bool]], Field(min_length=3)]

    @pytest.mark.parametrize("seed", SEEDS)
    def test_min_length_is_reached(self, seed):
        result = fake(self.Model, seed=seed, as_dict=False)
        assert result.flags == {True, False}
        assert len(result.exact) == 5
        assert result.choices == {"a", "b", "c"}
        assert set(result.keys) == {True, False}
        assert result.maybe == {True, False, None}

    def test_impossible_min_length_raises(self):
        class M(BaseModel):
            flags: Annotated[Set[bool], Field(min_length=3)]

        with pytest.raises(InvalidConstraints, match="distinct"):
            fake(M, seed=1)

    def test_union_of_unbounded_types(self):
        class M(BaseModel):
            values: Annotated[Set[Union[int, bool]], Field(min_length=4)]

        assert len(fake(M, seed=1, as_dict=False).values) >= 4

    def test_impossible_int_range_raises(self):
        class M(BaseModel):
            values: Annotated[
                Set[Annotated[int, Field(ge=1, le=2)]], Field(min_length=3)
            ]

        with pytest.raises(InvalidConstraints, match="distinct"):
            fake(M, seed=1)


@pytest.mark.pyfake
@pytest.mark.complex
class TestJsonSchemaExtra:
    def test_callable_json_schema_extra_is_ignored(self):
        def extra(schema):
            schema["examples"] = ["x"]

        class M(BaseModel):
            name: str = Field(json_schema_extra=extra)

        assert isinstance(fake(M, seed=1)["name"], str)


@pytest.mark.pyfake
@pytest.mark.complex
class TestDecimalDigits:
    class Model(BaseModel):
        plain: Decimal
        digits: Decimal = Field(max_digits=4)
        money: condecimal(max_digits=6, decimal_places=2)
        large: condecimal(max_digits=3, ge=100)

    @pytest.mark.parametrize("seed", SEEDS)
    def test_model_is_valid(self, seed):
        result = Pyfake(self.Model, seed=seed).generate()
        # Unbounded decimals get 2 decimal places, not a float's ~50 digits
        assert result["plain"] == result["plain"].quantize(Decimal("0.01"))
        assert result["large"] >= 100
