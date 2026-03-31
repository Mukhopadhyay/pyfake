import pytest
from pyfake import Pyfake
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
