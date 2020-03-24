from abc import abstractmethod, ABCMeta
from typing import Dict, Optional, Tuple


class _ReturnType(metaclass=ABCMeta):

    @abstractmethod
    def assert_is_superset(self, _type: Optional["_ReturnType"]) -> None:
        ...  # pragma: no cover

    @abstractmethod
    def downcast_result(self, result: Tuple[Tuple, Dict]) -> Tuple[Tuple, Optional[Dict]]:
        ...  # pragma: no cover
