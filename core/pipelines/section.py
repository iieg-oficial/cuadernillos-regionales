from abc import ABC, abstractmethod


class Section(ABC):
    @abstractmethod
    def run(self, municipio_id: str) -> dict:
        pass
