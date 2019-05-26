from typing import Any
from pakkr.returns._meta import _Meta
from pakkr.returns._no_return import _NoReturn
from pakkr.returns._return import _Return


def returns(*args, **kwargs):
    """Decorator to add the __pakkr_returns__ attribute to the object being decorated"""
    if not (args or kwargs):
        return_obj = _NoReturn()
    elif not args and kwargs:
        return_obj = _Meta(**kwargs)
    elif args:
        return_obj = _Return(args, _Meta(**kwargs) if kwargs else None)

    def decorated(obj):
        obj.__pakkr_returns__ = return_obj
        return obj
    return decorated


def collapse(returns):
    """Collapse or roll-up a sequence of "return" types into one"""
    final_args = [Any]
    final_meta = {}

    for ret in returns:
        if isinstance(ret, _Meta):
            final_args = []
            final_meta.update(ret)
        elif isinstance(ret, _Return):
            final_args = ret.values
            final_meta.update(ret.meta or {})
        elif isinstance(ret, _NoReturn):
            final_args = []
        elif ret is Any:
            final_args = [Any]
        else:
            raise RuntimeError("Unexpected return type {}".format(ret))

    if final_args:
        return _Return(final_args, _Meta(**final_meta) if final_meta else None)
    elif final_meta:
        return _Meta(**final_meta)
    else:
        return _NoReturn()
