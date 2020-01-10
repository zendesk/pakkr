from typing import Dict, Iterable, Tuple, Union

from ._meta import _Meta


class _Return:
    """
    Class that describes how to interpret the return value(s) of a Callable.
    Positional arguments are treated as types of return value(s) and keyword
    arguments are treated as metadata and their types.
    """
    __slots__ = ('values', 'meta', '_types')

    def __init__(self, values, meta=None):
        if not values:
            if meta:
                raise RuntimeError("'values' is empty, use _Meta instead.")
            else:
                raise RuntimeError("'values' and 'meta' are empty, use _NoReturn instead.")

        if meta:
            assert isinstance(meta, _Meta), f"meta '{meta}' is not an instance of _Meta"

        super().__init__()
        self.values = tuple(values)
        self.meta = meta
        self._types = list(values)
        if meta:
            self._types.append(meta)

    def parse_result(self, result: Tuple[Tuple, Dict]) -> Tuple[Tuple, Dict]:
        """
        Verify the return value of a Callable matches what this instance describes.

        Parameters
        ----------
        result : Tuple[Tuple, Dict]

        Returns
        -------
        Tuple[Tuple, Dict]
            return[0]: actual results or positional arguments for the next Callable
            return[1]: updated metadata for the Callables to follow

        Raises
        ------
        RuntimeError
            when mis-match in shape or type
        """
        if len(self._types) > 1:
            assert isinstance(result, Tuple), f"Returned value '{result}' is not an instance of Tuple"
            if len(result) != len(self._types):
                raise RuntimeError("Expecting {} values, but only {} were returned."
                                   .format(len(self._types), len(result)))

        if len(self._types) == 1:
            result = (result,)

        args = []
        meta = {}
        wrong_type_args = []
        for item, _type in zip(result, self._types):
            if hasattr(_type, "parse_result"):
                sub_args, sub_meta = _type.parse_result(item)
                args += sub_args
                meta.update(sub_meta)
            elif hasattr(_type, '__origin__') and _type.__origin__:
                if (
                        _type.__origin__ == Union and
                        isinstance(item, _type.__args__)
                ):
                    args.append(item)
                elif isinstance(item, _type.__origin__):
                    args.append(item)
            elif isinstance(item, _type):
                args.append(item)
            else:
                wrong_type_args.append((item, _type))

        if wrong_type_args:
            msg = " and ".join("'{}' is not of type {}".format(item, _type)
                               for item, _type in wrong_type_args)
            raise RuntimeError("Values error: {}.".format(msg))

        return tuple(args), meta

    def assert_is_superset(self, _type):
        """
        Assert this instance is a superset of the given _type.

        Parameters
        ----------
        _type : None or an _Return, _Meta, _NoReturn instance

        Returns
        -------
        None

        Raises
        ------
        RuntimeError
            when this instance is not a superset of _type
        """

        if not _type:
            return

        if isinstance(_type, _Meta):
            if not self.meta:
                raise RuntimeError('{} is not a superset of {}.'.format(self, _type))

            self.meta.assert_is_superset(_type)
            return

        if isinstance(_type, _Return):
            if self.values != _type.values:
                raise RuntimeError("Return values are not the same '{}' vs '{}'."
                                   .format(self.values, _type.values))

            self.meta.assert_is_superset(_type.meta)

    def downcast_result(self, result: Tuple[Tuple, Dict]) -> Tuple[Tuple, Dict]:
        """
        Downcast the return value of a Callable to what this instance defines.

        Parameters
        ----------
        result : Tuple[Tuple, Dict]

        Returns
        -------
        Tuple[Tuple, Dict]
            return[0]: downcasted results or positional arguments for the next Callable
            return[1]: downcasted metadata for the Callables to follow

        Raises
        ------
        RuntimeError
            when mis-match in shape or type, or ambigous conversion
        """

        assert result and isinstance(result, Tuple), f"Value '{result}' is not an instance of Tuple"
        values = result[0]
        if self.values and len(self.values) != len(values):
            raise RuntimeError("Cannot downcast {} to {}".format(values, self.values))

        new_values = []
        new_meta = None
        for value, _type in zip(values, self.values):
            if isinstance(value, _type):
                new_values.append(value)
            else:
                raise RuntimeError("Cannot downcast {} to {}".format(values, self.values))

        if self.meta:
            _, new_meta = self.meta.downcast_result(result)

        return tuple(new_values), new_meta

    def __repr__(self):
        return "({}, {})".format(self.values, self.meta)

    def __eq__(self, other):
        if isinstance(other, _Return):
            return self.values == other.values and self.meta == other.meta
        return False
