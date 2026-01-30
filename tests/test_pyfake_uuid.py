import pytest
import uuid

from pyfake import Pyfake
import pydantic
from pydantic import BaseModel, Field
from typing import Optional, Annotated


@pytest.mark.uuid
class TestPyfakeUUIDGeneration:

    class StressTestUUIDModel(BaseModel):
        native_uuid: uuid.UUID
        native_uuid_default_factory: uuid.UUID = Field(default_factory=uuid.uuid4)

        uuid1: pydantic.UUID1
        uuid3: pydantic.UUID3
        uuid4: pydantic.UUID4
        uuid5: pydantic.UUID5
        uuid6: pydantic.UUID6
        uuid7: pydantic.UUID7
        uuid8: pydantic.UUID8
        uuid_optional: Optional[uuid.UUID]

    def _as_uuid(self, value):
        if isinstance(value, uuid.UUID):
            return value
        return uuid.UUID(str(value))

    @pytest.mark.parametrize(
        "seed",
        list(range(10))
        + [
            None,
        ],
    )
    def test_pyfake_uuid_versions(self, seed):
        pyfake = Pyfake(self.StressTestUUIDModel, seed=seed)
        result = pyfake.generate()

        assert isinstance(result, dict)

        # Convert to UUID objects for consistent assertions
        native_uuid = self._as_uuid(result["native_uuid"])
        native_uuid_default_factory = self._as_uuid(
            result["native_uuid_default_factory"]
        )
        u1 = self._as_uuid(result["uuid1"])
        u3 = self._as_uuid(result["uuid3"])
        u4 = self._as_uuid(result["uuid4"])
        u5 = self._as_uuid(result["uuid5"])
        u6 = self._as_uuid(result["uuid6"])
        u7 = self._as_uuid(result["uuid7"])
        u8 = self._as_uuid(result["uuid8"])

        assert isinstance(native_uuid, uuid.UUID)
        assert isinstance(native_uuid_default_factory, uuid.UUID)
        assert isinstance(u1, uuid.UUID)
        assert isinstance(u3, uuid.UUID)
        assert isinstance(u4, uuid.UUID)
        assert isinstance(u5, uuid.UUID)
        assert isinstance(u6, uuid.UUID)
        assert isinstance(u7, uuid.UUID)
        assert isinstance(u8, uuid.UUID)

        # Check UUID versions
        assert native_uuid.version == 4
        assert native_uuid_default_factory.version == 4
        assert u1.version == 1
        assert u3.version == 3
        assert u4.version == 4
        assert u5.version == 5
        # custom implementations should set their versions
        assert u6.version == 6
        assert u7.version == 7
        assert u8.version == 8

        # optional may be None or a UUID
        assert result["uuid_optional"] is None or isinstance(
            self._as_uuid(result["uuid_optional"]), uuid.UUID
        )
