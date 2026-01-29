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


class TestPyfakeInstantiation:

    class SampleModel(BaseModel):
        integer_basic: int
        string_basic: str

    def test_pyfake_return_type(self):
        pyfake = Pyfake(self.SampleModel)
        assert isinstance(pyfake.generate(num=1), dict)
        assert isinstance(pyfake.generate(num=5), list)

    def test_pyfake_return_count(self):
        pyfake = Pyfake(self.SampleModel)

        multiple_result = pyfake.generate(num=5)

        assert len(multiple_result) == 5
