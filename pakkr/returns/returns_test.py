import pytest
from pakkr.returns._meta import _Meta
from pakkr.returns._no_return import _NoReturn
from pakkr.returns._return import _Return
from pakkr.returns.returns import collapse, returns
from typing import Any


def test_returns_deco():
    decorated = returns()(lambda: 1)
    assert isinstance(decorated.__pakkr_returns__, _NoReturn)

    decorated = returns(int)(lambda: 1)
    assert isinstance(decorated.__pakkr_returns__, _Return)
    assert str(decorated.__pakkr_returns__) == "((<class 'int'>,), None)"

    decorated = returns(x=bool)(lambda: 1)
    assert isinstance(decorated.__pakkr_returns__, _Meta)
    assert str(decorated.__pakkr_returns__) == "{'x': <class 'bool'>}"

    decorated = returns(int, x=bool)(lambda: 1)
    assert isinstance(decorated.__pakkr_returns__, _Return)
    assert str(decorated.__pakkr_returns__) == "((<class 'int'>,), {'x': <class 'bool'>})"


def test_collapse():
    assert collapse([_Meta(x=int)]) == _Meta(x=int)
    assert collapse([_Return([int], _Meta(x=str))]) == _Return([int], _Meta(x=str))
    assert collapse([_NoReturn()]) == _NoReturn()

    assert collapse([_Meta(x=int), _Return([int], _Meta(y=str))]) == \
        _Return([int], _Meta(x=int, y=str))

    assert collapse([_Return([int], _Meta(y=str)), _NoReturn()]) == _Meta(y=str)
    assert collapse([_Return([int], _Meta(y=str)), Any]) == _Return([Any], _Meta(y=str))

    with pytest.raises(RuntimeError) as e:
        collapse([int])
    assert str(e.value) == "Unexpected return type <class 'int'>"
