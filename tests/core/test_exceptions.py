import pytest
from pyfake.exceptions import PyfakeError, GeneratorNotFound, InvalidConstraints


@pytest.mark.pyfake
@pytest.mark.exceptions
class TestExceptions:

    def test_generator_not_found_is_pyfake_error(self):
        exc = GeneratorNotFound("int")
        assert isinstance(exc, PyfakeError)
        assert isinstance(exc, Exception)

    def test_generator_not_found_message_contains_type(self):
        exc = GeneratorNotFound("mytype")
        assert "mytype" in str(exc)

    def test_generator_not_found_can_be_raised(self):
        with pytest.raises(GeneratorNotFound):
            raise GeneratorNotFound("someType")

    def test_generator_not_found_is_caught_as_pyfake_error(self):
        with pytest.raises(PyfakeError):
            raise GeneratorNotFound("someType")

    def test_invalid_constraints_is_pyfake_error(self):
        exc = InvalidConstraints("bad constraint")
        assert isinstance(exc, PyfakeError)
        assert isinstance(exc, Exception)

    def test_invalid_constraints_message(self):
        msg = "value must be positive"
        exc = InvalidConstraints(msg)
        assert msg in str(exc)

    def test_invalid_constraints_can_be_raised(self):
        with pytest.raises(InvalidConstraints):
            raise InvalidConstraints("invalid")

    def test_invalid_constraints_is_caught_as_pyfake_error(self):
        with pytest.raises(PyfakeError):
            raise InvalidConstraints("invalid")
