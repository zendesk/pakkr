from typing import Dict, Tuple
import typing


class _Meta(dict):
    """
    Class that interprets the return value(s) of a Callable as metadata.
    Return values are mapped to metadata using a dictionary containing the
    types of the return values keyed by the metadata key name.
    """

    def __init__(self, *args, **kwargs):
        if not kwargs:
            raise RuntimeError("No meta key/type given.")

        super().__init__(*args, **kwargs)

        for value in kwargs.values():
            if not (hasattr(value, '__module__') and value.__module__ == 'typing'):
                assert isinstance(value, type), f"Value '{value}' is not a type nor in typing types"

    def parse_result(self, result: Dict) -> Tuple[Tuple, Dict]:
        """
        Verify the return value of a Callable matches what this instance describes.

        Parameters
        ----------
        result : Dict

        Returns
        -------
        Tuple[Tuple, Dict]
            return[0]: always an empty Tuple
            return[1]: metadata for the Callables to follow

        Raises
        ------
        RuntimeError
            when missing or extra keys or mis-match in expected types
        """
        assert isinstance(result, Dict), f"Meta should be a dictionary not {type(result)}"
        this_keys = set(self.keys())
        that_keys = set(result.keys())
        missing = this_keys - that_keys
        extra = that_keys - this_keys
        if missing or extra:
            msg = "Missing meta keys {}.".format(missing) if missing else ""
            msg += " " if msg and extra else ""
            msg += "Unexpected meta keys {}.".format(extra) if extra else ""
            raise RuntimeError(msg)

        def _check_t(k, t):
            if hasattr(t, '__origin__') and t.__origin__:
                if t.__origin__ == typing.Union:
                    return isinstance(result[k], t.__args__)
                else:
                    return isinstance(result[k], t.__origin__)  # i.e. List[int]
            else:
                return isinstance(result[k], t)

        wrong_types = [(k, t, type(result[k])) for k, t in self.items() if not _check_t(k, t)]

        if wrong_types:
            template = "key '{}' should be type {} but {} was returned"
            msg = " and ".join(template.format(*t) for t in wrong_types)
            raise RuntimeError("Meta error: {}.".format(msg))
        return ((), result)

    def assert_is_superset(self, _type):
        """
        Assert this instance is a superset of the given _type.

        Parameters
        ----------
        _type : None or _Meta instance

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

        if not isinstance(_type, _Meta):
            raise RuntimeError('{} is not a superset of {}.'.format(self, _type))

        diff = set(_type.keys()) - set(self.keys())
        if diff:
            raise RuntimeError('{} is not a superset of {}.'.format(self, _type))

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
        result = result[1]
        assert isinstance(result, Dict), f"Meta should be a dictionary not {type(result)}"
        meta = {}
        for key, _type in self.items():
            if key not in result:
                raise RuntimeError("Key '{}' does not exist in {}".format(key, result))
            item = result[key]
            if not isinstance(item, _type):
                raise RuntimeError("'{}' is not of type {}.".format(item, _type))

            meta[key] = item
        return (), meta
