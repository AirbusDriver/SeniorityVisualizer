import abc
from typing import List, Optional, Generic, TypeVar, Any, Dict

T = TypeVar("T")


class BaseSerializer(abc.ABC, Generic[T]):
    """Abstract class defining interface for any serialization"""

    @abc.abstractmethod
    def to_dict(self, obj: T) -> Dict[str, Any]:
        pass
