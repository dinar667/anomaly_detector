# coding: utf-8

from typing import Optional

from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QDialog

from core.services.prediction import PredictionServiceFactory
from gui.generated.ui_image_dialog import Ui_ImageDialog
from gui.view_models.event import Event
from gui.view_models.image_vm import ImageViewModel


class ImageDialog(QDialog, Ui_ImageDialog):
    def __init__(
        self, image_vm: Optional[ImageViewModel] = None, *args, **kwargs
    ) -> None:
        super().__init__(*args, **kwargs)

        self.setupUi(self)

        if image_vm is None:
            return

        self.image_vm: ImageViewModel = image_vm
        self.image_vm.subscribe(self.on_image_vm_updated)

        self.setup_ui()

    def setup_ui(self) -> None:
        self.setup_title()
        self.setup_images()
        self.update_results()

    def setup_title(self) -> None:
        self.setWindowTitle(f"{self.image_vm.path.name}")

    def setup_images(self) -> None:
        self.setup_src_image()
        self.setup_attention_image()

    def setup_src_image(self) -> None:
        vm = self.image_vm

        pixmap = QPixmap(vm.path.as_posix())
        self.srcImageLabel.setPixmap(pixmap)
        self.srcImageLabel.setMask(pixmap.mask())

    def setup_attention_image(self) -> None:
        vm = self.image_vm

        service = PredictionServiceFactory.create()
        attention = service.attention(vm.image)
        pixmap = QPixmap(attention.path.as_posix())
        self.attentionImageLabel.setPixmap(pixmap)
        self.srcImageLabel.setMask(pixmap.mask())

    def update_results(self) -> None:
        result = self.image_vm.result
        self.normalLabel.setText(f"{result.normal:>.4%}")
        self.pneumoniaLabel.setText(f"{result.pneumonia:>.4%}")

    def on_image_vm_updated(
        self, image_vm: ImageViewModel, event: Event
    ) -> None:
        if event is Event.ResultUpdated:
            self.update_results()
