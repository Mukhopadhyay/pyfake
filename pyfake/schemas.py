"""
Pydantic classes for various models used in PyFake
"""

from pydantic import BaseModel
from typing import Literal, Dict, List, Optional, Any
from collections.abc import Callable

types_ = Literal["integer", "null"]


class ModelType(BaseModel):
    type: types_


class ModelPropertySchema(BaseModel):
    title: str
    # If multi type then anyOf will be there
    anyOf: Optional[List[ModelType]] = None
    # If scalar type then type will be present
    type: Optional[types_] = None
    default: Optional[Any] = None


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
