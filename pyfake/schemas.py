"""
Pydantic classes for various models used in PyFake
"""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict


class FieldSchema(BaseModel):
    # title: Optional[str] = None
    type: str | None = None
    description: str | None = None  # description
    examples: list[Any] | None = None  # examples
    exclusiveMinimum: int | float | None = None  # lt
    exclusiveMaximum: int | float | None = None  # gt
    minimum: int | float | None = None  # ge
    maximum: int | float | None = None  # le
    default: Any | None = None  # default
    pattern: str | None = None  # pattern
    multipleOf: float | None = None  # multiple_of
    decimal_places: int | None = None  # decimal_places
    minLength: int | None = None  # min_length
    maxLength: int | None = None  # max_length
    format: str | None = None  # format


@dataclass
class GeneratorArgs:
    """
    The arguments that will be passed to the generator functions
    """

    # Bounds can be numbers, Decimals, dates, datetimes, times or timedeltas
    lt: Any | None = None
    gt: Any | None = None
    le: Any | None = None
    ge: Any | None = None
    default: Any | None = None
    pattern: str | None = None
    multiple_of: Any | None = None
    decimal_places: int | None = None
    max_digits: int | None = None
    min_length: int | None = None
    max_length: int | None = None
    examples: list[Any] | None = (
        None  # Will be handled by the registry not the generators
    )
    format: str | None = None
    timezone: Any | None = None


class AnyOfSchema(FieldSchema):
    pass
    # type: types_


class ModelPropertySchema(FieldSchema):
    title: str | None = None
    # If multi type then anyOf will be there
    anyOf: list[AnyOfSchema] | None = None

    # Allow extra to True
    model_config = ConfigDict(extra="allow")


class ModelJSONSchema(BaseModel):
    properties: dict[str, ModelPropertySchema]
    type: Literal["object"]
    required: list[str]
    title: str


class ResolvedSchema(BaseModel):
    """
    The expectations of the generators after resolving the schema
    """

    type: str
    generator_func: Callable[..., Any] | None = None
    args: GeneratorArgs
