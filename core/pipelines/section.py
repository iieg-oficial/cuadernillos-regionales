from abc import ABC, abstractmethod

from core.utils.regions import Region


class Section(ABC):
    @abstractmethod
    def run(self, region: Region) -> dict:
        pass
