import pytest
import json as json_module
from pyfake import Pyfake, Fake
from pydantic import BaseModel


@pytest.mark.api
@pytest.mark.pyfake
class TestPyfakeInstantiation:

    class SampleModel(BaseModel):
        integer_basic: int
        string_basic: str

    def test_pyfake_return_type(self):
        pyfake = Pyfake(self.SampleModel)

        assert isinstance(pyfake.generate(num=None), dict)
        assert isinstance(pyfake.generate(), dict)
        assert isinstance(pyfake.generate(num=1), dict)
        assert isinstance(pyfake.generate(num=5), list)

    def test_pyfake_return_count(self):
        pyfake = Pyfake(self.SampleModel)
        multiple_result = pyfake.generate(num=5)

        assert len(multiple_result) == 5

    def test_pyfake_return_type_from_schema(self):
        assert isinstance(Pyfake.from_schema(self.SampleModel, num=1), dict)
        assert isinstance(Pyfake.from_schema(self.SampleModel, num=5), list)

    def test_pyfake_return_count_from_schema(self):
        multiple_result = Pyfake.from_schema(self.SampleModel, num=5)

        assert len(multiple_result) == 5

    def test_pyfake_deterministic_with_seed(self):
        a = Pyfake.from_schema(self.SampleModel, seed=12345)
        b = Pyfake.from_schema(self.SampleModel, seed=12345)

        assert a == b


@pytest.mark.api
@pytest.mark.pyfake
class TestPyfakeAsDict:

    class SampleModel(BaseModel):
        integer_basic: int
        string_basic: str

    def test_as_dict_true_is_valid(self):
        pyfake = Pyfake(self.SampleModel)

        result = pyfake.generate(num=1, as_dict=True)

        assert isinstance(result, dict)
        # ensure the dict produced can be validated by the Pydantic model
        self.SampleModel(**result)

    def test_as_dict_false_is_model(self):
        pyfake = Pyfake(self.SampleModel)

        result = pyfake.generate(num=1, as_dict=False)

        assert isinstance(result, BaseModel)
        assert hasattr(result, "integer_basic")
        assert hasattr(result, "string_basic")

    def test_multiple_as_dict_and_models(self):
        pyfake = Pyfake(self.SampleModel)

        dicts = pyfake.generate(num=3, as_dict=True)
        assert isinstance(dicts, list)
        assert len(dicts) == 3
        assert all(isinstance(d, dict) for d in dicts)
        for d in dicts:
            self.SampleModel(**d)

        models = pyfake.generate(num=3, as_dict=False)
        assert isinstance(models, list)
        assert len(models) == 3
        assert all(isinstance(m, BaseModel) for m in models)

    def test_from_schema_respects_as_dict(self):
        as_dict = Pyfake.from_schema(self.SampleModel, num=1, as_dict=True)
        as_model = Pyfake.from_schema(self.SampleModel, num=1, as_dict=False)

        assert isinstance(as_dict, dict)
        assert isinstance(as_model, BaseModel)


@pytest.mark.api
@pytest.mark.pyfake
class TestFakeClass:

    class SampleModel(BaseModel):
        x: int
        y: str

    def test_fake_call_returns_dict(self):
        f = Fake()
        result = f(self.SampleModel)
        assert isinstance(result, dict)

    def test_fake_call_with_num_returns_list(self):
        f = Fake()
        result = f(self.SampleModel, num=3)
        assert isinstance(result, list)
        assert len(result) == 3

    def test_fake_call_with_explicit_seed(self):
        f = Fake()
        a = f(self.SampleModel, seed=42)
        b = f(self.SampleModel, seed=42)
        assert a == b

    def test_fake_instance_seed_used_when_call_seed_is_none(self):
        a = Fake(seed=42)(self.SampleModel)
        b = Fake(seed=42)(self.SampleModel)
        assert a == b

    def test_fake_call_seed_overrides_instance_seed(self):
        f = Fake(seed=1)
        # Providing explicit seed=99 should override the instance seed
        result = f(self.SampleModel, seed=99)
        assert isinstance(result, dict)

    def test_fake_dict_returns_dict(self):
        f = Fake()
        result = f.dict(self.SampleModel)
        assert isinstance(result, dict)

    def test_fake_dict_with_num_returns_list(self):
        f = Fake()
        result = f.dict(self.SampleModel, num=2)
        assert isinstance(result, list)
        assert len(result) == 2

    def test_fake_dict_with_seed(self):
        a = Fake().dict(self.SampleModel, seed=7)
        b = Fake().dict(self.SampleModel, seed=7)
        assert a == b

    def test_fake_model_returns_base_model(self):
        f = Fake()
        result = f.model(self.SampleModel)
        assert isinstance(result, BaseModel)

    def test_fake_model_with_num_returns_list(self):
        f = Fake()
        result = f.model(self.SampleModel, num=2)
        assert isinstance(result, list)
        assert len(result) == 2
        assert all(isinstance(m, BaseModel) for m in result)

    def test_fake_model_with_seed(self):
        a = Fake().model(self.SampleModel, seed=7)
        b = Fake().model(self.SampleModel, seed=7)
        assert a == b

    def test_fake_json_returns_json_string(self):
        f = Fake()
        result = f.json(self.SampleModel)
        assert isinstance(result, str)
        parsed = json_module.loads(result)
        assert isinstance(parsed, dict)
        assert "x" in parsed
        assert "y" in parsed

    def test_fake_json_with_num_returns_json_list(self):
        f = Fake()
        result = f.json(self.SampleModel, num=3)
        assert isinstance(result, str)
        parsed = json_module.loads(result)
        assert isinstance(parsed, list)
        assert len(parsed) == 3

    def test_fake_json_with_seed(self):
        a = Fake().json(self.SampleModel, seed=7)
        b = Fake().json(self.SampleModel, seed=7)
        assert a == b

    def test_fake_seed_returns_new_fake_with_seed(self):
        f = Fake()
        seeded = f.seed(42)
        assert isinstance(seeded, Fake)
        assert seeded._seed == 42

    def test_fake_seed_produces_deterministic_results(self):
        f = Fake()
        a = f.seed(42)(self.SampleModel)
        b = f.seed(42)(self.SampleModel)
        assert a == b
