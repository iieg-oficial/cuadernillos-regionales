from abc import ABC, abstractmethod
from typing import Any


class Stage(ABC):
    @abstractmethod
    def execute(self, input_data: Any = None) -> Any:
        pass
