from pydantic import BaseModel, Field
from typing import Annotated, Union


class Model(BaseModel):
    title: str = Field(title="Model Title")
    frozen: str = Field(frozen=True)
    description: str = Field(description="This is a description of the model.")
    alias: str = Field(alias="model_alias")
    examples: str = Field(examples=["example1", 1])
    examples_annotated: Annotated[Union[str, int], Field(examples=["example2", 2])]
    gt: int = Field(gt=10)
    lt: int = Field(lt=100)
    ge: int = Field(ge=5)
    le: int = Field(le=200)
    default: int = Field(default=42)
    multi_default: Annotated[Union[int, str], Field(default=99)]
    pattern: str = Field(pattern=r"^[a-zA-Z0-9_]+$")
    allow_inf_nan: float = Field(allow_inf_nan=False)
    multiple_of: int = Field(multiple_of=3)
    decimal_places: float = Field(decimal_places=2)
    min_length: str = Field(min_length=3)
    max_length: str = Field(max_length=50)
