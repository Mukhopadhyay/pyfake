"""
Pydantic classes for various models used in PyFake
"""

from pydantic import BaseModel
from typing import Literal, Dict, List, Optional, Any, Union
from collections.abc import Callable

types_ = Literal["integer", "null"]


class FieldSchema(BaseModel):
    # title: Optional[str] = None
    type: Optional[str] = None
    description: Optional[str] = None
    examples: Optional[List[Any]] = None
    exclusiveMinimum: Optional[Union[int, float]] = None
    exclusiveMaximum: Optional[Union[int, float]] = None
    minimum: Optional[Union[int, float]] = None
    maximum: Optional[Union[int, float]] = None
    default: Optional[Any] = None
    pattern: Optional[str] = None
    multipleOf: Optional[float] = None
    decimal_places: Optional[int] = None
    minLength: Optional[int] = None
    maxLength: Optional[int] = None


class AnyOfSchema(FieldSchema):
    type: types_


class ModelPropertySchema(FieldSchema):
    title: str
    # If multi type then anyOf will be there
    anyOf: Optional[List[AnyOfSchema]] = None
    # If scalar type then type will be present
    # type: Optional[types_] = None
    # default: Optional[Any] = None  # Default will always be outside anyOf


class ModelJSONSchema(BaseModel):
    properties: Dict[str, ModelPropertySchema]
    type: Literal["object"]
    required: List[str]
    title: str


class ResolverArgs(BaseModel):
    """
    The arguments that will be passed to the generator functions
    """

    lt: Optional[int] = None
    gt: Optional[int] = None
    le: Optional[int] = None
    ge: Optional[int] = None
    lte: Optional[int] = None
    gte: Optional[int] = None
    default: Optional[int] = None
    is_optional: Optional[bool] = False


class ResolvedSchema(BaseModel):
    """
    The expectations of the generators after resolving the schema
    """

    type: types_
    generator_func: Optional[Callable] = None
    args: ResolverArgs
