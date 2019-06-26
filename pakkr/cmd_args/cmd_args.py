from argparse import ArgumentParser
from functools import partial, reduce
from inspect import Parameter as iParameter, signature
from typing import Any, Callable, List
from .argument import _Argument


ATTR_CMD_ARGS = "__pakkr_cmd_args__"
ALLOWD_PARAMETER_KINDS = (iParameter.POSITIONAL_ONLY,
                          iParameter.POSITIONAL_OR_KEYWORD,
                          iParameter.KEYWORD_ONLY)


def _add_arguments_factory(arguments: List[_Argument]) -> Callable[[ArgumentParser], ArgumentParser]:
    return lambda parser: reduce(lambda p, argument: argument(p), arguments, parser)


def cmd_args(*arguments: _Argument) -> Any:
    """
    Decorator to add a function of Callable[[ArgumentParser], ArgumentParser] to the
    ATTR_CMD_ARGS attribute to the object being decorated.

    Parameters
    ----------
    arguments : List[_Argument]

    Returns
    -------
    Any
        The object being decorated
    """
    def decorate(obj):
        if hasattr(obj, ATTR_CMD_ARGS):
            raise RuntimeError(f'{ATTR_CMD_ARGS} has been set on {obj} already')
        _add_arguments = _add_arguments_factory(arguments)
        _verify_arguments(_add_arguments, obj)
        if isinstance(obj, type):
            fn = lambda self, parser: _add_arguments(parser)
        else:
            fn = _add_arguments
        setattr(obj, ATTR_CMD_ARGS, fn)
        return obj
    return decorate


def _verify_arguments(add_arguments, obj):
    parser = ArgumentParser(add_help=False)
    parser = add_arguments(parser)
    params = signature(obj.__call__ if isinstance(obj, type) else obj).parameters
    for action in parser._actions:
        if action.dest not in params:
            raise RuntimeError(f"'{action.dest}' is not an argument of the Callable.")
        elif params[action.dest].kind not in ALLOWD_PARAMETER_KINDS:
            raise RuntimeError(f"'{action.dest}' should be a positional or keyword argument of the Callable.")
