import abc
from typing import List, Optional, Generic, TypeVar, Any, Dict
import json
import datetime as dt

import pandas as pd

T = TypeVar("T")


class BaseSerializer(abc.ABC, Generic[T]):
    """Abstract class defining interface for any serialization"""

    @abc.abstractmethod
    def to_dict(self, obj: T) -> Dict[str, Any]:
        pass

    def to_json(self, obj: T) -> str:
        """Return a JSON string from an object"""
        return json.dumps(self.to_dict(obj), default=self.default)

    @staticmethod
    def default(obj):
        if isinstance(obj, dt.date):
            return obj.isoformat()

        return obj
