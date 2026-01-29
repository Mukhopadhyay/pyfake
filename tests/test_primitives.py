from pyfake.generators import primitives


class TestGenerateNone:

    def test_generate_none(self):
        assert primitives.generate_none() is None

    def test_generate_none_args_kwargs(self):
        assert primitives.generate_none(1, thing="abc") is None
