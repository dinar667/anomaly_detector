from dataclasses import dataclass, field
from pathlib import Path
from typing import List

from core.models.prediction import Prediction


@dataclass
class Image:
    path: Path
    result: Prediction = field(default_factory=Prediction)


@dataclass(frozen=True)
class Images:
    _collection: List[Image]

    def add(self, image: Image) -> None:
        self._collection.append(image)

    def remove(self, image: Image) -> None:
        self._collection.remove(image)

    @property
    def last(self) -> Image:
        return self._collection[-1]

    @property
    def count(self) -> int:
        return len(self._collection)

    def __iter__(self):
        yield from self._collection

    def __contains__(self, item: Image) -> bool:
        return item in self._collection

    def __len__(self) -> int:
        return len(self._collection)
