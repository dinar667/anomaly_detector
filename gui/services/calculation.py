# coding: utf-8

import enum

from PyQt5.QtCore import QRunnable, QObject, pyqtSignal

from core.services.prediction import PredictionServiceFactory
from gui.view_models.image_vm import ImagesViewModel


class CalculationSignals(QObject):
    started = pyqtSignal()
    completed = pyqtSignal()
    failed = pyqtSignal(str)
    progress = pyqtSignal(int, int)
    cancelled = pyqtSignal()


class CalculationStatus(enum.Enum):
    Calculation = enum.auto()
    Pending = enum.auto()
    Cancelled = enum.auto()
    Completed = enum.auto()


class CalculationService(QRunnable):
    def __init__(self, images_vm: ImagesViewModel) -> None:
        super().__init__()

        self.signals: CalculationSignals = CalculationSignals()
        self.status: CalculationStatus = CalculationStatus.Pending

        self.images_vm: ImagesViewModel = images_vm

    def run(self) -> None:
        self.signals.started.emit()
        self.status = CalculationStatus.Calculation
        try:
            self._run()
        except Exception as ex:
            self.signals.failed.emit(str(ex))

    def _run(self) -> None:
        service = PredictionServiceFactory.create()
        images = iter(self.images_vm)
        count: int = self.images_vm.count
        current: int = 0
        while True:
            while self.can_calculate():
                try:
                    image_vm = next(images)
                    prediction = service.predict(image_vm.image)
                    image_vm.set_prediction(prediction)
                    current += 1
                    self.signals.progress.emit(current, count)
                except StopIteration:
                    self.status = CalculationStatus.Completed
                    self.signals.completed.emit()
                    return

                if self.stopped():
                    self.signals.cancelled.emit()
                    return

    def pause(self) -> None:
        self.status = CalculationStatus.Pending

    def resume(self) -> None:
        self.status = CalculationStatus.Calculation

    def stop(self) -> None:
        self.status = CalculationStatus.Cancelled

    def paused(self) -> bool:
        return self.status is CalculationStatus.Pending

    def stopped(self) -> None:
        return self.status is CalculationStatus.Cancelled

    def can_calculate(self) -> bool:
        return self.status not in {
            CalculationStatus.Pending,
            CalculationStatus.Completed,
            CalculationStatus.Cancelled,
        }
