# coding: utf-8
from pathlib import Path
from typing import List

from dataclasses import dataclass, field

from core.models.image import Image, Images
from core.models.prediction import Prediction
from gui.view_models.base_vm import BaseViewModel, notifying
from gui.view_models.event import Event


@dataclass(frozen=True)
class ImageViewModel(BaseViewModel):
    image: Image

    @property
    def path(self) -> Path:
        return self.image.path

    @property
    def result(self) -> Prediction:
        return self.image.result

    @notifying(event=Event.ResultUpdated)
    def set_prediction(self, result: Prediction) -> None:
        self.image.result = result


@dataclass(frozen=True)
class ImagesViewModel(BaseViewModel):
    images: Images
    vms: List[ImageViewModel] = field(default_factory=list)

    @notifying(event=Event.ImageAdded)
    def add(self, image: Image) -> None:
        self.images.add(image)
        self.create_vm(image)

    def create_vm(self, image: Image) -> None:
        image_vm = ImageViewModel([], image)
        self.vms.append(image_vm)

    @notifying(event=Event.ImageRemoved)
    def remove_vm(self, image_vm: ImageViewModel) -> None:
        if image_vm in self.vms:
            image = image_vm.image
            self.vms.remove(image_vm)

            if image in self.images:
                self.images.remove(image)

    @property
    def last_image(self) -> Image:
        return self.images.last

    @property
    def last_image_vm(self) -> ImageViewModel:
        return self.vms[-1]

    @property
    def count(self) -> int:
        return self.images.count

    def __iter__(self):
        yield from self.vms
