import pytest
from typing import Any
from ._meta import _Meta
from ._no_return import _NoReturn
from ._return import _Return


def test_no_return_parse_result():
    n = _NoReturn()

    assert n.parse_result(None) == ((), {})

    with pytest.raises(RuntimeError) as e:
        n.parse_result(_Return((int,), None))
    assert str(e.value) == "Do not expect value other than None."

    with pytest.raises(RuntimeError) as e:
        n.parse_result(_Meta(a=str))
    assert str(e.value) == "Do not expect value other than None."


def test_no_return_assert_is_superset():
    n = _NoReturn()

    n.assert_is_superset(None)
    n.assert_is_superset(_NoReturn())

    with pytest.raises(RuntimeError) as e:
        n.assert_is_superset(_Return((Any,), _Meta(a=int)))
    assert str(e.value) == "_NoReturn is not a superset of ((typing.Any,), {'a': <class 'int'>})."

    with pytest.raises(RuntimeError) as e:
        n.assert_is_superset(_Meta(y=str))
    assert str(e.value) == "_NoReturn is not a superset of {'y': <class 'str'>}."

    with pytest.raises(RuntimeError) as e:
        n.assert_is_superset(int)
    assert str(e.value) == "_NoReturn is not a superset of <class 'int'>."


def test_no_return_downcast_result():
    n = _NoReturn()

    assert n.downcast_result(None) == ((), {})
    assert n.downcast_result(int) == ((), {})
    assert n.downcast_result(((1, "str"), {'x': True})) == ((), {})
    assert n.downcast_result({'x': True}) == ((), {})
