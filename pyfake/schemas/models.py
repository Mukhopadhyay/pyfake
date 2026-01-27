"""
Pydantic classes for various models used in PyFake
"""

from pydantic import BaseModel
from typing import Literal, Dict, List, Optional
from collections.abc import Callable


class ModelPropertySchema(BaseModel):
    title: str
    type: Literal["integer"]


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


class ResolvedSchema(BaseModel):
    """
    The expectations of the generators after resolving the schema
    """

    generator_func: Callable
    args: ResolverArgs
