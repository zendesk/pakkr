import sys
import traceback
from contextlib import contextmanager
from itertools import chain


@contextmanager
def exception_handler(exc_handler):
    "Sets a custom exception handler for the scope of a 'with' block."
    sys.excepthook = exc_handler
    try:
        yield
    finally:
        sys.excepthook = sys.__excepthook__


def pakkr_exchandler(_type, ex, tb):
    cause = ex.__cause__
    if cause:
        traceback.print_exception(_type, cause, cause.__traceback__, chain=False)
        print(ex.pakkr_stacks())
    else:
        traceback.print_exception(_type, ex, ex.__traceback__, chain=False)


class PakkrError(Exception):
    def __init__(self, message, stack=None):
        self._message = message
        self._stacks = [stack] if stack else []
        super(PakkrError, self).__init__(message, stack)

    def append_stack(self, stack):
        self._stacks.append(stack)
        return self

    def __str__(self):
        return self._message + '\n' + self.pakkr_stacks()

    def pakkr_stacks(self):
        return '\n'.join(self._stacks)


def exception_context(identifier, arg, opts, meta):
    called_with = ', '.join(chain([str(type(v)) for v in arg],
                                  ['{}={}'.format(k, type(v)) for k, v in opts.items()]))
    available_meta = ''
    if meta:
        available_meta = '\n\t\tavailable meta {}'.format(summarise_dictionary(meta))

    return '\tinside {identifier} executed with ({called_with}){available_meta}'.format(
        identifier=identifier,
        called_with=called_with,
        available_meta=available_meta)


def summarise_dictionary(obj):
    return '{{{}}}'.format(', '.join(['{}: {}'.format(k, type(v)) for k, v in obj.items()]))
