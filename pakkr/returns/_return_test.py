from typing import Callable, Generator, List, Optional, Union

import pytest

from ..pipeline import Pipeline
from ._meta import _Meta
from ._no_return import _NoReturn
from ._return import _Return


def test_returns():
    r = _Return([int, str], _Meta(x=bool))
    assert str(r) == "((<class 'int'>, <class 'str'>), {'x': <class 'bool'>})"

    r = _Return([int, str], None)
    assert str(r) == "((<class 'int'>, <class 'str'>), None)"

    with pytest.raises(RuntimeError) as e:
        _Return([], _Meta(x=int))
    assert str(e.value) == "'values' is empty, use _Meta instead."

    with pytest.raises(RuntimeError) as e:
        _Return([], None)
    assert str(e.value) == "'values' and 'meta' are empty, use _NoReturn instead."

    r = _Return([Optional[int]], _Meta(x=bool))
    assert str(r) == "((typing.Union[int, NoneType],), {'x': <class 'bool'>})"

    r = _Return([Union[str, int, float]], _Meta(x=Callable))
    assert str(r) == "((typing.Union[str, int, float],), {'x': typing.Callable})"

    r = _Return([Callable], _Meta(x=int))
    assert str(r) == "((typing.Callable,), {'x': <class 'int'>})"

    r = _Return([Generator], _Meta(x=int))
    assert str(r) == "((typing.Generator,), {'x': <class 'int'>})"


def test_return_eq():
    assert _Return([int, str], _Meta(x=bool)) == _Return([int, str], _Meta(x=bool))
    assert _Return([int, str], None) == _Return([int, str])
    assert _Return([int], None) != _Meta(x=int)


def test_return_parse_result():
    r = _Return([str], None)
    assert r.parse_result("hello") == (("hello",), {})

    r = _Return([int, str], _Meta(x=bool))
    assert r.parse_result((1, "hello", {"x": False})) == ((1, "hello"), {"x": False})

    with pytest.raises(AssertionError) as e:
        r.parse_result(1)
    assert str(e.value) == "Returned value '1' is not an instance of Tuple"

    with pytest.raises(RuntimeError) as e:
        r.parse_result((1, {'x': True}))
    assert str(e.value) == "Expecting 3 values, but only 2 were returned."

    with pytest.raises(RuntimeError) as e:
        r.parse_result(('hello', 1, {'x': True}))
    assert str(e.value) == ("Values error: 'hello' is not of type <class 'int'> and "
                            "'1' is not of type <class 'str'>.")

    r = _Return([List[int]], None)
    assert r.parse_result([1, 2]) == (([1, 2],), {})

    r = _Return([Optional[int]], _Meta(x=bool))
    assert r.parse_result((1, {"x": False})) == ((1,), {"x": False})
    assert r.parse_result((None, {"x": False})) == ((None,), {"x": False})

    r = _Return([Union[str, int, float]], _Meta(x=Callable))
    assert r.parse_result((1.0, {"x": Pipeline})) == ((1.0,), {'x': Pipeline})
    assert r.parse_result(('Wow', {"x": Pipeline})) == (('Wow',), {'x': Pipeline})

    r = _Return([Callable], _Meta(x=int))
    assert r.parse_result((Pipeline, {"x": 1})) == ((Pipeline,), {'x': 1})

    gen = (i for i in range(3))
    r = _Return([Generator], _Meta(x=int))
    assert r.parse_result((gen, {"x": 1})) == ((gen,), {'x': 1})


def test_return_assert_is_superset():
    r = _Return([int, str], _Meta(x=bool, y=int))

    r.assert_is_superset(None)
    r.assert_is_superset(_NoReturn())
    r.assert_is_superset(_Meta(x=bool))
    r.assert_is_superset(_Return([int, str], _Meta(x=bool)))

    with pytest.raises(RuntimeError) as e:
        r.assert_is_superset(_Return([int], _Meta(x=bool)))
    assert str(e.value) == ("Return values are not the same '(<class 'int'>, <class 'str'>)'"
                            " vs '(<class 'int'>,)'.")

    with pytest.raises(RuntimeError) as e:
        r.assert_is_superset(_Return([int, str], _Meta(x=bool, z=dict)))
    assert str(e.value) == ("{'x': <class 'bool'>, 'y': <class 'int'>} is not a superset of "
                            "{'x': <class 'bool'>, 'z': <class 'dict'>}.")

    with pytest.raises(RuntimeError) as e:
        r.assert_is_superset(_Meta(x=bool, z=dict))
    assert str(e.value) == ("{'x': <class 'bool'>, 'y': <class 'int'>} is not a superset of "
                            "{'x': <class 'bool'>, 'z': <class 'dict'>}.")

    r = _Return([int, str])
    with pytest.raises(RuntimeError) as e:
        r.assert_is_superset(_Meta(x=int))
    assert str(e.value) == ("((<class 'int'>, <class 'str'>), None) "
                            "is not a superset of {'x': <class 'int'>}.")


def test_return_downcast_result():
    r = _Return([int], None)
    assert r.downcast_result(([1], None)) == ((1,), None)
    assert r.downcast_result(([1], {'x': 1})) == ((1,), None)

    r = _Return([int, str], _Meta(x=bool))
    assert r.downcast_result(([1, 'hello'], {'x': True, 'y': 1})) == ((1, 'hello'), {'x': True})

    with pytest.raises(AssertionError) as e:
        r.downcast_result(1)
    assert str(e.value) == "Value '1' is not an instance of Tuple"

    with pytest.raises(RuntimeError) as e:
        r.downcast_result(([1], {'x': True}))
    assert str(e.value) == "Cannot downcast [1] to (<class 'int'>, <class 'str'>)"

    with pytest.raises(RuntimeError) as e:
        r.downcast_result(([1, 2], {}))
    assert str(e.value) == "Cannot downcast [1, 2] to (<class 'int'>, <class 'str'>)"
