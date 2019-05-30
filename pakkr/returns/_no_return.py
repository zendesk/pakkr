from typing import Dict, Tuple


class _NoReturn:
    """
    Class that specify a Callable has no return value
    """

    def parse_result(self, result: None) -> Tuple[Tuple, Dict]:
        """
        Verify the return value of a Callable is None.

        Parameters
        ----------
        result : None

        Returns
        -------
        Tuple[Tuple, Dict]
            return[0]: always an empty Tuple
            return[1]: always an emtpy Dict

        Raises
        ------
        RuntimeError
            the given value is not None
        """
        if result is not None:
            raise RuntimeError("Do not expect value other than None.")
        return (), {}

    def assert_is_superset(self, _type):
        """
        Assert this instance is a superset of the given _type.

        Parameters
        ----------
        _type : None or _NoReturn instance

        Returns
        -------
        None

        Raises
        ------
        RuntimeError
            when _type is not None or an _NoReturn instance
        """
        if not isinstance(_type, _NoReturn) and _type is not None:
            raise RuntimeError('_NoReturn is not a superset of {}.'.format(_type))

    def downcast_result(self, result: Tuple[Tuple, Dict]) -> Tuple[Tuple, Dict]:
        """
        Downcast the return value of a Callable to nothing.

        Parameters
        ----------
        result : Tuple[Tuple, Dict]

        Returns
        -------
        Tuple[Tuple, Dict]
            return[0]: always an empty Tuple
            return[1]: always an empty Dict
        """
        return (), {}

    def __eq__(self, other):
        return isinstance(other, _NoReturn)

    def __bool__(self):
        return False
