import json
import pathlib
from datetime import datetime
from typing import Any

import pytest
from pydantic import BaseModel, Field, ValidationError

from pyfake import Fake, GeneratorContext, Pyfake, fake
from pyfake.core.context import Context
from pyfake.exceptions import GeneratorNotFound, InvalidOverride, PyfakeError


class Address(BaseModel):
    street: str
    city: str


class User(BaseModel):
    email: str
    age: int = Field(ge=0, le=120)
    address: Address


class Profile(BaseModel):
    user: User
    nickname: str


class Account(BaseModel):
    primary: Address | None
    previous: list[Address] = Field(min_length=2, max_length=4)


class Dog(BaseModel):
    bark: str


class Cat(BaseModel):
    meow: str


class Owner(BaseModel):
    pet: Dog | Cat


@pytest.mark.pyfake
@pytest.mark.api
class TestScalarOverrides:
    def test_overrides_mapping(self):
        result = fake(User, overrides={"email": "a@b.com"})
        assert result["email"] == "a@b.com"

    def test_keyword_shorthand(self):
        result = fake(User, email="a@b.com", age=30)
        assert result["email"] == "a@b.com"
        assert result["age"] == 30

    def test_mapping_and_shorthand_combine(self):
        result = fake(User, overrides={"email": "a@b.com"}, age=30)
        assert (result["email"], result["age"]) == ("a@b.com", 30)

    def test_other_fields_are_still_generated(self):
        result = fake(User, email="a@b.com")
        assert isinstance(result["age"], int)
        assert set(result["address"]) == {"street", "city"}

    def test_plain_value_is_the_same_in_every_row(self):
        rows = fake(User, num=5, email="a@b.com")
        assert [row["email"] for row in rows] == ["a@b.com"] * 5

    def test_dict(self):
        assert fake.dict(User, email="a@b.com")["email"] == "a@b.com"
        assert fake.dict(User, overrides={"email": "x@y.com"})["email"] == "x@y.com"

    def test_model(self):
        result = fake.model(User, email="a@b.com")
        assert isinstance(result, User)
        assert result.email == "a@b.com"

    def test_json(self):
        assert json.loads(fake.json(User, email="a@b.com"))["email"] == "a@b.com"

    def test_pyfake_generate(self):
        result = Pyfake(User).generate(overrides={"email": "a@b.com"})
        assert result["email"] == "a@b.com"

    def test_empty_overrides(self):
        assert set(fake(User, overrides={})) == {"email", "age", "address"}

    def test_override_with_a_whole_nested_model(self):
        address = {"street": "Main", "city": "Pune"}
        assert fake(User, address=address)["address"] == address


@pytest.mark.pyfake
@pytest.mark.api
class TestCallableOverrides:
    def test_receives_generator_context(self):
        seen: list[GeneratorContext] = []

        def email(ctx: GeneratorContext) -> str:
            seen.append(ctx)
            return "a@b.com"

        now = datetime(2026, 1, 1)
        Pyfake(User, context=Context(seed=1, now=now)).generate(
            overrides={"email": email, "address.city": email}
        )

        assert [ctx.path for ctx in seen] == ["User.email", "User.address.city"]
        assert [ctx.type for ctx in seen] == [str, str]
        assert all(ctx.now == now for ctx in seen)
        assert all(isinstance(ctx, GeneratorContext) for ctx in seen)

    def test_context_random_is_the_seeded_stream(self):
        seen: list[Any] = []
        f = Fake(seed=3)
        f(User, email=lambda ctx: seen.append(ctx.random) or "a@b.com")
        assert f._context is not None
        assert seen == [f._context.random]

    def test_called_once_per_row(self):
        calls: list[str] = []

        def email(ctx: GeneratorContext) -> str:
            calls.append(ctx.path)
            return f"user{len(calls)}@b.com"

        rows = fake(User, num=4, email=email)
        assert len(calls) == 4
        assert [row["email"] for row in rows] == [f"user{i}@b.com" for i in range(1, 5)]

    def test_random_values_differ_per_row(self):
        rows = fake(User, num=30, seed=1, age=lambda ctx: ctx.random.randint(18, 65))
        ages = [row["age"] for row in rows]
        assert all(18 <= age <= 65 for age in ages)
        assert len(set(ages)) > 1

    def test_reproducible_with_call_seed(self):
        age = {"age": lambda ctx: ctx.random.randint(18, 65)}
        assert fake(User, num=5, seed=7, overrides=age) == fake(
            User, num=5, seed=7, overrides=age
        )

    def test_reproducible_with_seeded_instance(self):
        def age(ctx: GeneratorContext) -> int:
            return ctx.random.randint(18, 65)

        a, b = Fake(seed=2), Fake(seed=2)
        assert [a(User, age=age) for _ in range(3)] == [
            b(User, age=age) for _ in range(3)
        ]

    def test_wrapped_callable_sets_a_callable_value(self):
        class M(BaseModel):
            fn: Any

        assert fake(M, fn=lambda ctx: len)["fn"] is len


@pytest.mark.pyfake
@pytest.mark.api
class TestNestedOverrides:
    def test_nested_field(self):
        result = fake(User, overrides={"address.city": "Pune"})
        assert result["address"]["city"] == "Pune"
        assert isinstance(result["address"]["street"], str)

    def test_deeply_nested_field(self):
        result = fake(Profile, overrides={"user.address.city": "Pune"})
        assert result["user"]["address"]["city"] == "Pune"

    def test_nested_and_top_level_together(self):
        result = fake(
            Profile,
            overrides={"nickname": "nick", "user.email": "a@b.com", "user.age": 40},
        )
        assert result["nickname"] == "nick"
        assert result["user"]["email"] == "a@b.com"
        assert result["user"]["age"] == 40

    def test_nested_callable_runs_per_row(self):
        rows = fake(
            User,
            num=20,
            seed=1,
            overrides={"address.city": lambda ctx: ctx.random.choice("ab")},
        )
        assert {row["address"]["city"] for row in rows} == {"a", "b"}

    def test_through_optional(self):
        rows = fake(Account, num=30, seed=1, overrides={"primary.city": "Pune"})
        primaries = [row["primary"] for row in rows]
        assert any(p is None for p in primaries)
        assert all(p["city"] == "Pune" for p in primaries if p is not None)

    def test_through_list(self):
        result = fake(Account, overrides={"previous.city": "Pune"})
        assert 2 <= len(result["previous"]) <= 4
        assert all(item["city"] == "Pune" for item in result["previous"])

    def test_through_list_path(self):
        seen: set[str] = set()

        def city(ctx: GeneratorContext) -> str:
            seen.add(ctx.path)
            return "Pune"

        fake(Account, overrides={"previous.city": city})
        assert seen == {"Account.previous[].city"}

    def test_through_dict_and_tuple(self):
        class M(BaseModel):
            by_name: dict[str, Address] = Field(min_length=1, max_length=2)
            pair: tuple[Address, Address]

        result = fake(M, overrides={"by_name.city": "Pune", "pair.city": "Goa"})
        assert all(a["city"] == "Pune" for a in result["by_name"].values())
        assert [a["city"] for a in result["pair"]] == ["Goa", "Goa"]

    def test_union_of_models_applies_where_the_field_exists(self):
        rows = fake(Owner, num=30, seed=1, overrides={"pet.bark": "woof"})
        pets = [row["pet"] for row in rows]
        assert any("meow" in p for p in pets)
        assert all(p["bark"] == "woof" for p in pets if "bark" in p)

    def test_self_referencing_model(self):
        class Node(BaseModel):
            name: str
            child: "Node | None" = None

        result = fake(Node, seed=1, overrides={"name": "root"})
        assert result["name"] == "root"


@pytest.mark.pyfake
@pytest.mark.api
class TestOverrideErrors:
    def test_invalid_override_is_a_pyfake_value_error(self):
        assert issubclass(InvalidOverride, PyfakeError)
        assert issubclass(InvalidOverride, ValueError)

    def test_unknown_field(self):
        with pytest.raises(InvalidOverride, match="Unknown field 'emial'") as exc:
            fake(User, emial="a@b.com")
        assert "Fields: email, age, address" in str(exc.value)

    def test_unknown_nested_field(self):
        with pytest.raises(InvalidOverride, match="Unknown field 'address.zip'") as exc:
            fake(User, overrides={"address.zip": "123"})
        assert "'Address' has no field 'zip'" in str(exc.value)

    def test_unknown_deep_field(self):
        with pytest.raises(InvalidOverride, match="'user.address.zip'"):
            fake(Profile, overrides={"user.address.zip": "123"})

    def test_nesting_into_a_non_model_field(self):
        with pytest.raises(InvalidOverride, match="'User.email' has no nested model"):
            fake(User, overrides={"email.domain": "b.com"})

    def test_parent_and_child_conflict(self):
        with pytest.raises(
            InvalidOverride, match="'address' and 'address.city' conflict"
        ):
            fake(User, overrides={"address": {}, "address.city": "Pune"})

    def test_union_of_models_needs_the_field_on_one_of_them(self):
        with pytest.raises(InvalidOverride, match="'pet.purr'"):
            fake(Owner, overrides={"pet.purr": "x"})

    @pytest.mark.parametrize("key", [1, "", None])
    def test_non_string_or_empty_key(self, key):
        with pytest.raises(InvalidOverride, match="Override keys must be field names"):
            fake(User, overrides={key: "x"})

    def test_checked_before_generating_with_num_zero(self):
        with pytest.raises(InvalidOverride):
            fake(User, num=0, emial="a@b.com")

    def test_checked_with_pyfake(self):
        with pytest.raises(InvalidOverride):
            Pyfake(User).generate(overrides={"emial": "a@b.com"})

    def test_key_given_twice(self):
        with pytest.raises(TypeError, match="'email' given both"):
            fake(User, overrides={"email": "a@b.com"}, email="x@y.com")


@pytest.mark.pyfake
@pytest.mark.api
class TestNameCollisions:
    class Settings(BaseModel):
        num: int
        seed: str
        as_dict: bool

    def test_parameter_names_keep_their_meaning(self):
        rows = fake(self.Settings, num=3, seed=1)
        assert len(rows) == 3
        assert all(isinstance(row["seed"], str) for row in rows)

    def test_fields_named_like_parameters_via_overrides(self):
        rows = fake(
            self.Settings,
            num=2,
            overrides={"num": 5, "seed": "abc", "as_dict": True},
        )
        assert rows == [{"num": 5, "seed": "abc", "as_dict": True}] * 2

    def test_field_named_overrides(self):
        class M(BaseModel):
            overrides: str

        assert fake(M, overrides={"overrides": "x"}) == {"overrides": "x"}


@pytest.mark.pyfake
@pytest.mark.api
class TestOverridesAndConstraints:
    def test_valid_value_passes(self):
        assert fake(User, age=120)["age"] == 120

    def test_value_breaking_a_constraint_raises(self):
        with pytest.raises(ValidationError):
            fake(User, age=500)

    def test_callable_breaking_a_constraint_raises(self):
        with pytest.raises(ValidationError):
            fake(User, age=lambda ctx: -1)

    def test_nested_value_is_validated(self):
        class Strict(BaseModel):
            code: str = Field(pattern=r"^[A-Z]{3}$")

        class M(BaseModel):
            inner: Strict

        assert fake(M, overrides={"inner.code": "ABC"}) == {"inner": {"code": "ABC"}}
        with pytest.raises(ValidationError):
            fake(M, overrides={"inner.code": "abc"})

    def test_override_wins_over_default(self):
        class M(BaseModel):
            active: bool = True

        assert fake(M, active=False) == {"active": False}

    def test_override_avoids_generator_not_found(self):
        class Upload(BaseModel):
            location: pathlib.Path

        with pytest.raises(GeneratorNotFound):
            fake(Upload)
        assert fake(Upload, location=pathlib.Path("/tmp/x")) == {
            "location": pathlib.Path("/tmp/x")
        }

    def test_field_with_alias_uses_field_name(self):
        class M(BaseModel):
            user_name: str = Field(alias="userName")

        assert fake(M, user_name="bob") == {"user_name": "bob"}
        with pytest.raises(InvalidOverride):
            fake(M, overrides={"userName": "bob"})

    def test_override_with_registered_generator(self):
        f = Fake()
        f.register(str, lambda ctx, **constraints: "generated")
        result = f(User, email="a@b.com")
        assert result["email"] == "a@b.com"
        assert result["address"]["city"] == "generated"
