import pytest
from ._meta import _Meta
from ._no_return import _NoReturn
from ._return import _Return
from typing import Any


def test_meta_args():
    with pytest.raises(RuntimeError) as e:
        _Meta(int)
    assert str(e.value) == "No meta key/type given."


def test_meta_empty():
    with pytest.raises(RuntimeError) as e:
        _Meta()
    assert str(e.value) == "No meta key/type given."

def test_meta_value_not_type():
    with pytest.raises(AssertionError) as e:
        _Meta(x=1)
    assert str(e.value) == "Value '1' is not a type"

def test_meta_parse_result():
    m = _Meta(x=int, y=str)
    assert m == {'x': int, 'y': str}
    assert m.parse_result({'x': 1, 'y': 'hello'}) == ((), {'x': 1, 'y': 'hello'})


def test_meta_missing_kwargs():
    m = _Meta(x=int)
    with pytest.raises(RuntimeError) as e:
        m.parse_result({})
    assert str(e.value) == "Missing meta keys {'x'}."


def test_meta_parse_not_dict():
    m = _Meta(x=int)
    with pytest.raises(AssertionError) as e:
        m.parse_result((1,))
    assert str(e.value) == "Meta should be a dictionary not <class 'tuple'>"


def test_meta_extra_kwargs():
    m = _Meta(x=int)
    with pytest.raises(RuntimeError) as e:
        m.parse_result({'x': 1, 'y': 2})
    assert str(e.value) == "Unexpected meta keys {'y'}."


def test_meta_missing_and_extra_kwargs():
    m = _Meta(x=int)
    with pytest.raises(RuntimeError) as e:
        m.parse_result({'y': 2})
    assert str(e.value) == "Missing meta keys {'x'}. Unexpected meta keys {'y'}."


def test_meta_wrong_types():
    m = _Meta(x=int)
    with pytest.raises(RuntimeError) as e:
        m.parse_result({'x': "hello"})
    assert str(e.value) == \
        "Meta error: key 'x' should be type <class 'int'> but <class 'str'> was returned."

    m = _Meta(x=int, y=str)
    with pytest.raises(RuntimeError) as e:
        m.parse_result({'x': "hello", 'y': 1})
    assert str(e.value) == \
        ("Meta error: key 'x' should be type <class 'int'> but <class 'str'> was returned"
         " and key 'y' should be type <class 'str'> but <class 'int'> was returned.")


def test_meta_assert_is_superset():
    m = _Meta(x=int, y=str)
    m.assert_is_superset(_Meta(x=int))
    m.assert_is_superset(_Meta(y=str))
    m.assert_is_superset(_NoReturn())
    m.assert_is_superset(None)

    with pytest.raises(RuntimeError) as e:
        m.assert_is_superset(_Return([Any], None))
    assert str(e.value) == ("{'x': <class 'int'>, 'y': <class 'str'>} is not a superset "
                            "of ((typing.Any,), None).")

    with pytest.raises(RuntimeError) as e:
        m.assert_is_superset(_Return([int, str], _Meta(x=int)))
    assert str(e.value) == ("{'x': <class 'int'>, 'y': <class 'str'>} is not a superset "
                            "of ((<class 'int'>, <class 'str'>), {'x': <class 'int'>}).")

    with pytest.raises(RuntimeError) as e:
        m.assert_is_superset(_Return([], _Meta(x=int)))
    assert str(e.value) == ("'values' is empty, use _Meta instead.")


def test_meta_downcast_result():
    m = _Meta(x=int)
    assert m.downcast_result((['abc'], {'x': 10, 'z': 'hello'})) == ((), {'x': 10})

    with pytest.raises(RuntimeError) as e:
        m.downcast_result(((), {'y': 1, 'z': 'hello'}))
    assert str(e.value) == "Key 'x' does not exist in {'y': 1, 'z': 'hello'}"

    with pytest.raises(AssertionError) as e:
        m.downcast_result(((), "abc"))
    assert str(e.value) == "Meta should be a dictionary not <class 'str'>"

    with pytest.raises(RuntimeError) as e:
        m.downcast_result(((), {'x': 'hello'}))
    assert str(e.value) == "'hello' is not of type <class 'int'>."
