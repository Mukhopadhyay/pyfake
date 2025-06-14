from pyfake import number


def test_integer():
    x = number.integer()
    assert isinstance(x, int)
