import pytest
from pyfake import Pyfake
from pydantic import BaseModel
from pydantic import BaseModel, Field
from typing import Annotated, Optional, Union


class TestPyfakeIntegerGeneration:

    class StressTestModel(BaseModel):
        integer_basic: int
        integer_optional: Optional[int]
        integer_with_bounds: Annotated[int, Field(ge=1, le=100)]
        integer_with_multiple_annotations: Union[
            Annotated[int, Field(ge=1, le=100)], Annotated[int, Field(ge=200, le=300)]
        ]
        integer_with_multiple_annotations: Union[
            Annotated[int, Field(ge=1, le=100, default=21)],
            Annotated[int, Field(ge=200, le=300, default=42)],
        ]
        integer_optional_2_defaults: Optional[
            Annotated[int, Field(ge=1, le=100, default=21)]
        ] = 42
        integer_optional_3_defaults: Union[
            Annotated[int, Field(ge=1, le=10, default=5)],
            Annotated[int, Field(ge=20, le=30, default=29)],
        ] = 27
        integer_optional_default: Optional[int] = 42

    @pytest.mark.parametrize(
        "seed",
        list(range(10))
        + [
            None,
        ],
    )
    def test_pyfake_stress_test_model(self, seed):
        pyfake = Pyfake(self.StressTestModel, seed=seed)
        result = pyfake.generate()

        assert isinstance(result, dict)

        assert isinstance(result["integer_basic"], int)
        assert isinstance(result["integer_optional"], (int, type(None)))

        assert isinstance(result["integer_basic"], int)
        assert isinstance(result["integer_optional"], (int, type(None)))
        assert 1 <= result["integer_with_bounds"] <= 100
        assert (
            1 <= result["integer_with_multiple_annotations"] <= 100
            or 200 <= result["integer_with_multiple_annotations"] <= 300
        )
        assert (
            1 <= result["integer_with_multiple_annotations"] <= 100
            or 200 <= result["integer_with_multiple_annotations"] <= 300
        )
        if result["integer_optional_2_defaults"] is not None:
            assert (
                result["integer_optional_2_defaults"] == 42
                or 1 <= result["integer_optional_2_defaults"] <= 100
            )
        if result["integer_optional_3_defaults"] is not None:
            assert (
                result["integer_optional_3_defaults"] == 27
                or 1 <= result["integer_optional_3_defaults"] <= 10
                or 20 <= result["integer_optional_3_defaults"] <= 30
            )
        assert isinstance(result["integer_optional_default"], (int, type(None)))


class TestPyfakeStringGeneration:

    class StressTestStringModel(BaseModel):
        string_basic: str
        string_optional: Optional[str]
        string_with_bounds: Annotated[str, Field(min_length=1, max_length=100)]
        string_with_multiple_annotations: Union[
            Annotated[str, Field(min_length=1, max_length=5)],
            Annotated[str, Field(min_length=10, max_length=15)],
        ]
        string_optional_default: Optional[
            Annotated[str, Field(min_length=1, max_length=10, default="abc")]
        ] = "xyz"
        string_with_length_default: Annotated[
            str, Field(min_length=3, max_length=3, default="abc")
        ] = "def"
        string_with_examples: Annotated[
            str, Field(examples=["example1", "example2", "example3"])
        ]

    @pytest.mark.parametrize(
        "seed",
        list(range(10))
        + [
            None,
        ],
    )
    def test_pyfake_stress_test_model(self, seed):
        pyfake = Pyfake(self.StressTestStringModel, seed=seed)
        result = pyfake.generate()

        assert isinstance(result, dict)

        assert isinstance(result["string_basic"], str)
        assert isinstance(result["string_optional"], (str, type(None)))
        assert 1 <= len(result["string_with_bounds"]) <= 100

        assert (
            1 <= len(result["string_with_multiple_annotations"]) <= 5
            or 10 <= len(result["string_with_multiple_annotations"]) <= 15
        )
        if result["string_optional_default"] is not None:
            assert (
                result["string_optional_default"] == "xyz"
                or 1 <= len(result["string_optional_default"]) <= 10
            )
        if result["string_with_length_default"] is not None:
            assert (
                result["string_with_length_default"] == "def"
                or len(result["string_with_length_default"]) == 3
            )
        # Ensure strings are alphabetic where generated
        assert all(c.isalpha() for c in result["string_basic"])


class TestPyfakeFloatGeneration:

    class StressTestFloatModel(BaseModel):
        float_basic: float
        float_optional: Optional[float]
        float_with_bounds: Annotated[float, Field(ge=1.0, le=100.0)]
        float_with_multiple_annotations: Union[
            Annotated[float, Field(ge=1.0, le=100.0)],
            Annotated[float, Field(ge=200.0, le=300.0)],
        ]
        float_with_defaults: Annotated[float, Field(ge=1.0, le=10.0, default=5.5)] = 6.6

    @pytest.mark.parametrize(
        "seed",
        list(range(10))
        + [
            None,
        ],
    )
    def test_pyfake_stress_test_model(self, seed):
        pyfake = Pyfake(self.StressTestFloatModel, seed=seed)
        result = pyfake.generate()

        assert isinstance(result, dict)

        assert isinstance(result["float_basic"], float)
        assert isinstance(result["float_optional"], (float, type(None)))
        assert 1.0 <= result["float_with_bounds"] <= 100.0
        assert (
            1.0 <= result["float_with_multiple_annotations"] <= 100.0
            or 200.0 <= result["float_with_multiple_annotations"] <= 300.0
        )
        if result["float_with_defaults"] is not None:
            assert (
                result["float_with_defaults"] == 6.6
                or 1.0 <= result["float_with_defaults"] <= 10.0
            )


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
