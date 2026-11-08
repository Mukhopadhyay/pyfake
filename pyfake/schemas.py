"""
Pydantic classes for various models used in PyFake
"""

from dataclasses import dataclass
from pydantic import BaseModel, ConfigDict
from typing import Literal, Dict, List, Optional, Any, Union
from collections.abc import Callable


class FieldSchema(BaseModel):
    # title: Optional[str] = None
    type: Optional[str] = None
    description: Optional[str] = None  # description
    examples: Optional[List[Any]] = None  # examples
    exclusiveMinimum: Optional[Union[int, float]] = None  # lt
    exclusiveMaximum: Optional[Union[int, float]] = None  # gt
    minimum: Optional[Union[int, float]] = None  # ge
    maximum: Optional[Union[int, float]] = None  # le
    default: Optional[Any] = None  # default
    pattern: Optional[str] = None  # pattern
    multipleOf: Optional[float] = None  # multiple_of
    decimal_places: Optional[int] = None  # decimal_places
    minLength: Optional[int] = None  # min_length
    maxLength: Optional[int] = None  # max_length
    format: Optional[str] = None  # format


@dataclass
class GeneratorArgs:
    """
    The arguments that will be passed to the generator functions
    """

    # Bounds can be numbers, Decimals, dates, datetimes, times or timedeltas
    lt: Optional[Any] = None
    gt: Optional[Any] = None
    le: Optional[Any] = None
    ge: Optional[Any] = None
    default: Optional[Any] = None
    pattern: Optional[str] = None
    multiple_of: Optional[Any] = None
    decimal_places: Optional[int] = None
    max_digits: Optional[int] = None
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    examples: Optional[List[Any]] = None  # Will be handled by the registry not the generators
    format: Optional[str] = None
    timezone: Optional[Any] = None


class AnyOfSchema(FieldSchema):
    pass
    # type: types_


class ModelPropertySchema(FieldSchema):
    title: Optional[str] = None
    # If multi type then anyOf will be there
    anyOf: Optional[List[AnyOfSchema]] = None

    # Allow extra to True
    model_config = ConfigDict(extra="allow")


class ModelJSONSchema(BaseModel):
    properties: Dict[str, ModelPropertySchema]
    type: Literal["object"]
    required: List[str]
    title: str


class ResolvedSchema(BaseModel):
    """
    The expectations of the generators after resolving the schema
    """

    type: str
    generator_func: Optional[Callable] = None
    args: GeneratorArgs
