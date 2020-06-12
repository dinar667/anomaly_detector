# coding: utf-8
import csv
from pathlib import Path
from typing import List, Optional

from PyQt5.QtCore import QMimeData, QUrl, QThreadPool
from PyQt5.QtGui import QDragEnterEvent, QDropEvent
from PyQt5.QtWidgets import QWidget

from core.models.image import Images, Image
from gui.generated.ui_main_widget import Ui_MainWidget
from gui.services.calculation import CalculationService
from gui.utils.dialogs import show_error_dialog
from gui.utils.fp import image_filepath_valid, save_file_dialog
from gui.view_models.event import Event
from gui.view_models.image_vm import ImagesViewModel, ImageViewModel


class MainWidget(QWidget, Ui_MainWidget):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.setupUi(self)

        self.threadpool = QThreadPool()
        self.threadpool.setMaxThreadCount(1)

        images = Images([])
        self.images_vm: ImagesViewModel = ImagesViewModel([], images)

        self.images_vm.subscribe(self.on_images_updated)

        self.calculation_service: Optional[CalculationService] = None

    # noinspection PyUnusedLocal
    def on_start_required(self, play_enabled: bool) -> None:
        if not self.images_vm.count:
            self.reset_play_button()
            return

        service = self.calculation_service
        if service is not None and not service.stopped():
            self.on_pause_required()
            return

        service = CalculationService(self.images_vm)
        service.signals.started.connect(self.on_calculation_started)
        service.signals.completed.connect(self.on_calculation_completed)
        service.signals.progress.connect(self.on_calculation_progress)
        service.signals.failed.connect(self.on_calculation_failed)
        service.signals.cancelled.connect(self.on_calculation_cancelled)
        self.calculation_service: CalculationService = service

        self.threadpool.start(self.calculation_service)

    def on_calculation_started(self) -> None:
        self.lock_interface()

    def on_calculation_completed(self) -> None:
        self.unlock_interface()
        self.reset_play_button()

    def on_calculation_progress(self, current: int, count: int) -> None:
        self.progressBar.setMaximum(count)
        self.progressBar.setValue(current)

    def on_calculation_failed(self, message: str) -> None:
        ...

    def on_calculation_cancelled(self) -> None:
        self.unlock_interface()
        self.reset_play_button()

    def on_pause_required(self) -> None:
        service = self.calculation_service
        if service is None:
            return

        if service.paused():
            self.calculation_service.resume()
        else:
            self.calculation_service.pause()

    def on_stop_required(self) -> None:
        if self.calculation_service is None:
            return

        self.calculation_service.stop()
        self.reset_play_button()

    def reset_play_button(self) -> None:
        self.startButton.blockSignals(True)
        self.startButton.setChecked(False)
        self.startButton.blockSignals(False)

    def on_save_required(self) -> None:
        filepath = save_file_dialog(self, "Сохранить таблицу", "*.csv")
        if not filepath.name:
            return

        self._save_table(filepath)

    def _save_table(self, filepath: Path) -> None:
        header, rows = self.tableWidget.dump()
        try:
            with open(
                filepath.as_posix(), mode="w", encoding="utf-8", newline=""
            ) as file:
                writer = csv.DictWriter(file, fieldnames=header, delimiter=";")
                writer.writeheader()
                writer.writerows(rows)
        except Exception as ex:
            show_error_dialog(self, text=f"Ошибка сохранения таблицы: {ex}")

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        mime_data: QMimeData = event.mimeData()
        if mime_data.hasUrls():
            event.accept()

    def dropEvent(self, event: QDropEvent) -> None:
        mime_data: QMimeData = event.mimeData()
        urls: List[QUrl] = mime_data.urls()

        if not len(urls):
            event.ignore()
            return

        for each in urls:
            filepath: Path = Path(each.toLocalFile())

            if not image_filepath_valid(filepath):
                continue

            image = Image(filepath)
            self.images_vm.add(image)

    def on_images_updated(self, vm: ImagesViewModel, event: Event) -> None:
        if event is Event.ImageAdded:
            self.tableWidget.add_image(vm.last_image_vm)
            self.countLabel.setText(f"{vm.count} шт.")
        elif event is Event.ImageRemoved:
            self.countLabel.setText(f"{vm.count} шт.")

    def set_interface_enabled(self, enabled: bool = True) -> None:
        self.saveButton.setEnabled(enabled)
        self.tableWidget.setEnabled(enabled)

    def lock_interface(self) -> None:
        self.set_interface_enabled(False)

    def unlock_interface(self) -> None:
        self.set_interface_enabled(True)

    def on_images_removing_started(self) -> None:
        ...

    def on_images_removed(self, images_vm: List[ImageViewModel]) -> None:
        for image_vm in images_vm:
            self.images_vm.remove_vm(image_vm)
