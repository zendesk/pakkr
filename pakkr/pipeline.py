import inspect
import logging
from functools import partial, reduce
from inspect import getfullargspec
from typing import Any, Callable
from pakkr.cmd_args.cmd_args import ATTR_CMD_ARGS
from pakkr.exception import (exception_handler,
                             exception_context,
                             PakkrError,
                             pakkr_exchandler,
                             summarise_dictionary)
from pakkr.logging import IndentationAdapter, log_timing
from pakkr.returns.returns import collapse

ATTR_RETURNS = "__pakkr_returns__"

pakkr_logger = logging.getLogger('pakkr')


class Pipeline:
    """Pipeline takes a sequences of callables and execute them when itself is
    being executed with parameters. Outputs of a callable is passed as inputs
    to the next callable. Pipeline also facilitates where an output(s) of a
    callable is required as input(s) to multiple callables that are not the
    immediate following callable."""

    def __init__(self, *steps, **kwargs):
        super().__init__()
        self._meta = {}
        self._steps = steps

        self.__steps_returns = self._collect_steps_returns()
        self.__set_pakkr_returns(None)

        self.__set_pakkr_cmd_args(self._add_steps_arguments)

        self._name = kwargs.pop("_name") if "_name" in kwargs else "unnamed_" + str(id(self))

    def __call__(self, *args, **meta):
        kwargs = meta.copy()  # shallow copy the original keyword arguments for error msg
        stack = _get_pakkr_stack()  # calling this here will guarantee to have at least one item
        logger = IndentationAdapter(pakkr_logger, {'indent': len(stack) - 1,
                                                   'identifier': _identifier(self)})
        self._meta = {}

        try:
            with log_timing(logger):
                partial_run_step = partial(self._run_step, indent=len(stack))
                new_arg, _ = reduce(partial_run_step, self._steps, (args, meta))
                new_arg, new_meta = self._filter_results((new_arg, self._meta))
        except PakkrError as e:
            with exception_handler(pakkr_exchandler):
                raise e.append_stack(exception_context(_identifier(self), args, kwargs, None))

        if len(stack) > 1:
            # if this pipeline is nested, we should return values as if this were a Callable
            if new_arg:
                return tuple(new_arg) + (new_meta,)
            else:
                return new_meta or None
        elif len(new_arg) == 1:
            return new_arg[0]
        else:
            return tuple(new_arg) or None

    def _filter_results(self, results):
        if self.__custom_returns is None:
            return results

        return self.__custom_returns.downcast_result(results)

    def _run_step(self, args_meta, step, indent):
        assert isinstance(step, Callable)

        args, meta = args_meta

        argspec = getfullargspec(step)

        kwargs = dict(zip(argspec.args[::-1], argspec.defaults or []))
        kwargs.update(meta)
        logger = IndentationAdapter(pakkr_logger, {'indent': indent,
                                                   'identifier': _identifier(step)})
        kwargs.update(logger=logger)

        # to handle instance/class bound methods
        skip_self = int((argspec.args or False) and
                        (hasattr(step, '__func__') or hasattr(step.__call__, '__func__')))
        try:
            opts = {key: kwargs[key] for key in argspec.args[skip_self + len(args):]}
        except KeyError as e:
            context = '\twhen executing {identifier}, available inputs/meta were {args}/{kwargs}'
            context = context.format(identifier=_identifier(step),
                                     args=tuple(map(type, args)),
                                     kwargs=summarise_dictionary(kwargs))
            msg = "{} is required but not available.".format(str(e))
            raise PakkrError(msg, context) from RuntimeError(msg)

        if argspec.varkw == 'meta':
            opts.update(kwargs)

        try:
            with log_timing(logger):
                result = step(*args, **opts)
        except PakkrError as e:
            raise e
        except Exception as e:
            context = exception_context(_identifier(step), args, opts, meta)
            raise PakkrError(str(e), context) from e

        new_meta = {}

        if hasattr(step, ATTR_RETURNS):
            returns = getattr(step, ATTR_RETURNS)
            result, new_meta = returns.parse_result(result)
        else:
            result = [result]

        self._meta.update(new_meta)
        meta.update(new_meta)

        return (result, meta)

    def _collect_steps_returns(self):
        return collapse(getattr(step, ATTR_RETURNS) if hasattr(step, ATTR_RETURNS) else Any
                        for step in self._steps)

    def __get_pakkr_returns(self):
        """The return values' types are usually the return values of the last step and the
        aggregation of meta values, unless the subset of those are explicitly set."""
        if self.__custom_returns is not None:
            return self.__custom_returns

        return self.__steps_returns

    def __set_pakkr_returns(self, _type):
        """Setting the return values' types in this context is mainly for removing the return
        values of the last step and/or reducing the number of meta values"""
        self.__steps_returns.assert_is_superset(_type)
        self.__custom_returns = _type

    __pakkr_returns__ = property(__get_pakkr_returns, __set_pakkr_returns)

    def _add_steps_arguments(self, parser):
        for step in self._steps:
            if hasattr(step, ATTR_CMD_ARGS):
                parser = getattr(step, ATTR_CMD_ARGS)(parser)
        return parser

    def __get_pakkr_cmd_args(self):
        return self.__custom_cmd_args

    def __set_pakkr_cmd_args(self, fn):
        self.__custom_cmd_args = fn

    __pakkr_cmd_args__ = property(__get_pakkr_cmd_args, __set_pakkr_cmd_args)

    def add_arguments(self, parser):
        return self.__pakkr_cmd_args__(parser)


def _get_pakkr_stack(stack=None):
    '''Get the sequence of running Pakkr Pipeline from the call stack.
    The call stack will contains all calling functions so we need to filter on
    frames that are executing functions belonging to Pipeline instances which is
    accessible via frame.f_locals['self'].
    Also the call stack is LIFO, so the sequence need to be reversed.
    '''
    stack = stack or inspect.stack()

    return [frame.f_locals['self']
            for (frame, _, _, func_name, _, _) in stack[::-1]
            if func_name == '__call__' and
            'self' in frame.f_locals and
            isinstance(frame.f_locals['self'], Pipeline)]


def _identifier(obj):
    attr = None
    if hasattr(obj, '_name'):
        attr = '_name'
    elif hasattr(obj, '__name__'):
        attr = '__name__'

    if attr:
        obj_name = getattr(obj, attr)
    else:
        obj_name = "unnamed_" + str(id(obj))

    return '"{obj_name}"<{obj_class}>'.format(obj_name=obj_name,
                                              obj_class=type(obj).__name__)
