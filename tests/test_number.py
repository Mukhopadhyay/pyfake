from pyfake import number


def test_integer():
    x = number.integer()
    assert isinstance(x, int)


def test_float():
    x = number.number()
    assert isinstance(x, float)
