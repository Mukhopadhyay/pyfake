import pathlib
import random
import uuid
from datetime import datetime
from typing import Annotated, Any

import pytest
from pydantic import UUID4, BaseModel, Field, ValidationError

import pyfake
from pyfake import Fake, GeneratorContext, Pyfake
from pyfake.core import registry
from pyfake.core.context import Context
from pyfake.exceptions import GeneratorNotFound


def path_gen(ctx: GeneratorContext, **constraints: Any) -> pathlib.Path:
    return pathlib.Path(f"/tmp/{ctx.random.randint(0, 10_000)}")


class Upload(BaseModel):
    location: pathlib.Path


class Uploads(BaseModel):
    location: pathlib.Path
    backup: pathlib.Path | None
    history: list[pathlib.Path]


class Flags(BaseModel):
    a: bool
    b: bool
    c: bool


@pytest.fixture(autouse=True)
def restore_global_generators():
    """Keep module-level registrations from leaking between tests"""
    saved = dict(registry._global_generators)
    registry._global_generators.clear()
    yield
    registry._global_generators.clear()
    registry._global_generators.update(saved)


@pytest.mark.pyfake
@pytest.mark.registry
class TestCustomType:
    def test_unsupported_type_without_registration_raises(self):
        with pytest.raises(GeneratorNotFound, match="Upload.location"):
            Fake()(Upload)

    def test_registered_type_is_generated(self):
        f = Fake()
        f.register(pathlib.Path, path_gen)

        result = f(Upload)
        assert isinstance(result, dict)
        assert isinstance(result["location"], pathlib.Path)

    def test_registered_type_returns_valid_model(self):
        f = Fake()
        f.register(pathlib.Path, path_gen)

        result = f.model(Upload)
        assert isinstance(result, Upload)
        assert isinstance(result.location, pathlib.Path)

    def test_registered_type_inside_optional_and_list(self):
        f = Fake()
        f.register(pathlib.Path, path_gen)

        for row in f(Uploads, num=20):
            assert isinstance(row["location"], pathlib.Path)
            assert row["backup"] is None or isinstance(row["backup"], pathlib.Path)
            assert all(isinstance(p, pathlib.Path) for p in row["history"])

    def test_register_returns_none(self):
        assert Fake().register(pathlib.Path, path_gen) is None
        assert pyfake.register(pathlib.Path, path_gen) is None


@pytest.mark.pyfake
@pytest.mark.registry
class TestGeneratorContext:
    def test_ctx_carries_field_metadata(self):
        now = datetime(2026, 1, 1)
        calls: list[GeneratorContext] = []

        def gen(ctx: GeneratorContext, **constraints: Any) -> pathlib.Path:
            calls.append(ctx)
            return pathlib.Path("/tmp/x")

        class M(BaseModel):
            location: pathlib.Path
            items: list[pathlib.Path] = Field(min_length=1, max_length=1)

        Pyfake(M, context=Context(now=now), generators={pathlib.Path: gen}).generate()

        assert [c.path for c in calls] == ["M.location", "M.items[]"]
        assert all(c.type is pathlib.Path for c in calls)
        assert all(c.now == now for c in calls)
        assert all(isinstance(c, GeneratorContext) for c in calls)

    def test_ctx_random_is_the_seeded_stream(self):
        seen: list[Any] = []

        def gen(ctx: GeneratorContext, **constraints: Any) -> pathlib.Path:
            seen.append(ctx.random)
            return pathlib.Path("/tmp/x")

        f = Fake(seed=3)
        f.register(pathlib.Path, gen)
        f(Upload)

        assert f._context is not None
        assert seen == [f._context.random]

    def test_ctx_is_frozen(self):
        ctx = GeneratorContext(
            random=random.Random(0),
            now=datetime(2026, 1, 1),
            path="M.x",
            type=int,
        )
        with pytest.raises(AttributeError):
            ctx.path = "other"  # type: ignore[misc]

    def test_only_set_constraints_are_passed(self):
        received: list[dict[str, Any]] = []

        def gen(ctx: GeneratorContext, **constraints: Any) -> str:
            received.append(constraints)
            return "abc"

        class M(BaseModel):
            name: str = Field(min_length=2, max_length=4)

        f = Fake()
        f.register(str, gen)
        f(M)
        assert received == [{"min_length": 2, "max_length": 4}]

    def test_unconstrained_field_gets_no_constraints(self):
        def gen(ctx: GeneratorContext) -> pathlib.Path:
            return pathlib.Path("/tmp/x")

        f = Fake()
        f.register(pathlib.Path, gen)
        assert f(Upload) == {"location": pathlib.Path("/tmp/x")}

    def test_registry_args_are_not_passed(self):
        received: list[dict[str, Any]] = []

        def gen(ctx: GeneratorContext, **constraints: Any) -> str:
            received.append(constraints)
            return "a@b.com"

        class M(BaseModel):
            email: str = Field(
                json_schema_extra={"format": "email"}, examples=["x@y.com"]
            )

        f = Fake()
        f.register(str, gen)
        assert f(M) == {"email": "a@b.com"}
        assert received == [{}]


@pytest.mark.pyfake
@pytest.mark.registry
class TestOverrideBuiltin:
    def test_override_bool(self):
        f = Fake()
        f.register(bool, lambda ctx, **c: True)
        assert all(row == {"a": True, "b": True, "c": True} for row in f(Flags, num=10))

    def test_override_str_but_not_other_types(self):
        class M(BaseModel):
            name: str
            age: int

        f = Fake()
        f.register(str, lambda ctx, **c: "fixed")
        for row in f(M, num=5):
            assert row["name"] == "fixed"
            assert isinstance(row["age"], int)

    def test_override_matches_exact_type_only(self):
        # bool is a subclass of int, but keeps its built-in generator
        f = Fake()
        f.register(int, lambda ctx, **c: 7)

        class M(BaseModel):
            n: int
            flag: bool

        for row in f(M, num=10):
            assert row["n"] == 7
            assert isinstance(row["flag"], bool)

    def test_override_uuid_covers_versioned_uuid_fields(self):
        fixed = uuid.UUID("12345678-1234-4234-8234-123456789abc")

        class M(BaseModel):
            plain: uuid.UUID
            v4: UUID4

        f = Fake()
        f.register(uuid.UUID, lambda ctx, **c: fixed)
        assert f(M) == {"plain": fixed, "v4": fixed}

    def test_override_takes_precedence_over_format(self):
        class M(BaseModel):
            email: str = Field(json_schema_extra={"format": "email"})

        f = Fake()
        f.register(str, lambda ctx, **c: "custom")
        assert f(M) == {"email": "custom"}

    def test_default_wins_over_registered_generator(self):
        class M(BaseModel):
            name: str = "default"

        f = Fake()
        f.register(str, lambda ctx, **c: "custom")
        assert f(M) == {"name": "default"}

    def test_constrained_annotated_field_uses_registered_generator(self):
        class M(BaseModel):
            n: Annotated[int, Field(ge=10, le=20)]

        received: list[dict[str, Any]] = []

        def gen(ctx: GeneratorContext, **constraints: Any) -> int:
            received.append(constraints)
            return ctx.random.randint(constraints["ge"], constraints["le"])

        f = Fake()
        f.register(int, gen)
        assert 10 <= f(M)["n"] <= 20
        assert received == [{"ge": 10, "le": 20}]

    def test_invalid_custom_value_fails_validation(self):
        f = Fake()
        f.register(int, lambda ctx, **c: "not an int")

        class M(BaseModel):
            n: int

        with pytest.raises(ValidationError):
            f(M)


@pytest.mark.pyfake
@pytest.mark.registry
class TestConflicts:
    def test_registering_again_replaces(self):
        f = Fake()
        f.register(str, lambda ctx, **c: "first")
        f.register(str, lambda ctx, **c: "second")

        class M(BaseModel):
            name: str

        assert f(M) == {"name": "second"}

    def test_global_registering_again_replaces(self):
        pyfake.register(str, lambda ctx, **c: "first")
        pyfake.register(str, lambda ctx, **c: "second")

        class M(BaseModel):
            name: str

        assert Fake()(M) == {"name": "second"}

    def test_instance_beats_global(self):
        pyfake.register(str, lambda ctx, **c: "global")
        f = Fake()
        f.register(str, lambda ctx, **c: "instance")

        class M(BaseModel):
            name: str

        assert f(M) == {"name": "instance"}
        assert Fake()(M) == {"name": "global"}

    def test_global_beats_builtin(self):
        pyfake.register(bool, lambda ctx, **c: False)
        assert Fake()(Flags) == {"a": False, "b": False, "c": False}


@pytest.mark.pyfake
@pytest.mark.registry
class TestSeededDeterminism:
    def make(self, seed: int | None = None) -> Fake:
        f = Fake(seed=seed)
        f.register(pathlib.Path, path_gen)
        return f

    def test_seeded_instances_match(self):
        assert self.make(seed=1)(Uploads, num=5) == self.make(seed=1)(Uploads, num=5)

    def test_different_seeds_differ(self):
        assert self.make(seed=1)(Uploads, num=5) != self.make(seed=2)(Uploads, num=5)

    def test_per_call_seed_is_reproducible(self):
        f = self.make()
        assert f(Uploads, num=5, seed=7) == f(Uploads, num=5, seed=7)

    def test_seeded_stream_is_reproducible(self):
        a, b = self.make(seed=4), self.make(seed=4)
        assert [a(Uploads) for _ in range(3)] == [b(Uploads) for _ in range(3)]

    def test_global_registration_is_reproducible(self):
        pyfake.register(pathlib.Path, path_gen)
        assert Fake(seed=9)(Uploads, num=5) == Fake(seed=9)(Uploads, num=5)


@pytest.mark.pyfake
@pytest.mark.registry
class TestRegistryIsolation:
    def test_instances_do_not_share_registrations(self):
        a, b = Fake(), Fake()
        a.register(pathlib.Path, path_gen)

        assert isinstance(a(Upload)["location"], pathlib.Path)
        with pytest.raises(GeneratorNotFound):
            b(Upload)

    def test_instance_registration_does_not_touch_globals(self):
        Fake().register(pathlib.Path, path_gen)
        assert registry._global_generators == {}

    def test_seed_keeps_registrations(self):
        f = Fake()
        f.register(pathlib.Path, path_gen)
        assert isinstance(f.seed(1)(Upload)["location"], pathlib.Path)

    def test_seed_copies_registrations(self):
        f = Fake()
        seeded = f.seed(1)
        f.register(pathlib.Path, path_gen)
        seeded.register(str, lambda ctx, **c: "seeded")

        with pytest.raises(GeneratorNotFound):
            seeded(Upload)

        class M(BaseModel):
            name: str

        assert f(M)["name"] != "seeded"

    def test_default_fake_instance(self, monkeypatch):
        monkeypatch.setattr(pyfake.fake, "_generators", {})
        pyfake.fake.register(pathlib.Path, path_gen)

        assert isinstance(pyfake.fake(Upload)["location"], pathlib.Path)
        with pytest.raises(GeneratorNotFound):
            Fake()(Upload)


@pytest.mark.pyfake
@pytest.mark.registry
class TestModuleLevelRegister:
    def test_visible_to_new_instances(self):
        pyfake.register(pathlib.Path, path_gen)
        assert isinstance(Fake()(Upload)["location"], pathlib.Path)
        assert isinstance(pyfake.fake(Upload)["location"], pathlib.Path)

    def test_visible_to_pyfake(self):
        pyfake.register(pathlib.Path, path_gen)
        assert isinstance(Pyfake(Upload).generate()["location"], pathlib.Path)
        assert isinstance(
            Pyfake.from_schema(Upload, as_dict=False).location,  # type: ignore[union-attr]
            pathlib.Path,
        )

    def test_pyfake_accepts_generators(self):
        result = Pyfake(Upload, generators={pathlib.Path: path_gen}).generate()
        assert isinstance(result["location"], pathlib.Path)


@pytest.mark.pyfake
@pytest.mark.registry
class TestRegisterValidation:
    @pytest.mark.parametrize("register", ["instance", "module"])
    def test_non_callable_raises(self, register):
        fn = Fake().register if register == "instance" else pyfake.register
        with pytest.raises(TypeError, match="callable"):
            fn(pathlib.Path, "not callable")  # type: ignore[arg-type]

    @pytest.mark.parametrize("register", ["instance", "module"])
    def test_unhashable_type_raises(self, register):
        fn = Fake().register if register == "instance" else pyfake.register
        with pytest.raises(TypeError, match="hashable"):
            fn(["not", "a", "type"], path_gen)

    def test_failed_registration_is_not_stored(self):
        with pytest.raises(TypeError):
            pyfake.register(pathlib.Path, None)  # type: ignore[arg-type]
        assert registry._global_generators == {}
