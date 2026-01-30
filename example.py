import warnings

warnings.filterwarnings("ignore")

from pyfake import Pyfake


from pydantic import UUID1, UUID3, UUID4, UUID5, UUID6, UUID7, UUID8
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, ConfigDict


class Model(BaseModel):
    alias_uuid: UUID = Field(alias="id")
    native_uuid: UUID
    native_uuid_default_factory: UUID = Field(default_factory=uuid4)
    pyd_uuid1: UUID1
    pyd_uuid3: UUID3
    pyd_uuid4: UUID4
    pyd_uuid5: UUID5
    pyd_uuid6: UUID6
    pyd_uuid7: UUID7
    pyd_uuid8: UUID8

    model_config = ConfigDict(json_encoders={UUID: str})


x = Pyfake.from_schema(Model, num=1)
print(x)
