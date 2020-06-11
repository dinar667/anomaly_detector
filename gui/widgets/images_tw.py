# coding: utf-8
from typing import List, Tuple, Dict

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QKeyEvent
from PyQt5.QtWidgets import (
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QTableWidgetSelectionRange,
)

from gui.view_models.event import Event
from gui.view_models.image_vm import ImageViewModel
from gui.widgets.image_dialog import ImageDialog


class ImageTitleTableWidget(QTableWidgetItem):
    def __init__(self, image_vm: ImageViewModel, *args) -> None:
        super().__init__(*args)

        self.setTextAlignment(Qt.AlignCenter)
        self.setText(f"{image_vm.path.name}")

        flags = self.flags()
        self.setFlags(flags & ~Qt.ItemIsEditable)

        self.image_vm: ImageViewModel = image_vm

    def clear(self) -> None:
        ...


class ResultTableWidgetItem(QTableWidgetItem):
    def __init__(self, image_vm: ImageViewModel, *args) -> None:
        super().__init__(*args)

        self.setTextAlignment(Qt.AlignCenter)

        flags = self.flags()
        self.setFlags(flags & ~Qt.ItemIsEditable)

        self.image_vm = image_vm
        self.image_vm.subscribe(self.on_image_updated)

        self.update_image_result(image_vm)

    def on_image_updated(self, image_vm: ImageViewModel, event: Event) -> None:
        if event is Event.ResultUpdated:
            self.update_image_result(image_vm)

    def update_image_result(self, image_vm: ImageViewModel) -> None:
        raise NotImplementedError()

    def clear(self):
        self.image_vm.unsubscribe(self.update_image_result)


class PneumoniaTableWidgetItem(ResultTableWidgetItem):
    def update_image_result(self, image_vm: ImageViewModel) -> None:
        result = image_vm.result
        self.setText(f"{result.pneumonia:>.4%}")


class NormalTableWidgetItem(ResultTableWidgetItem):
    def update_image_result(self, image_vm: ImageViewModel) -> None:
        result = image_vm.result
        self.setText(f"{result.normal:>.4%}")


class ImagesTableWidget(QTableWidget):
    rows_removing_started = pyqtSignal()
    rows_removed = pyqtSignal("PyQt_PyObject")

    def __init__(self, *args) -> None:
        super().__init__(*args)

        header: QHeaderView = self.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)

        # noinspection PyUnresolvedReferences
        self.cellDoubleClicked.connect(self.on_cell_double_clicked)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        key = event.key()
        if key == Qt.Key_Delete:
            self.remove_selected_rows()
        else:
            super().keyPressEvent(event)

    def remove_selected_rows(self) -> None:
        self.rows_removing_started.emit()

        ranges: List[QTableWidgetSelectionRange] = self.selectedRanges()
        offset: int = 0

        for r in ranges:
            first = r.topRow() - offset
            last = r.bottomRow() - offset

            deleted_images = []
            for row in range(last, first - 1, -1):
                image_vm: ImageViewModel = self.item(row, 0).image_vm
                image_vm.clear_subscriptions()
                deleted_images.append(image_vm)

                self.removeRow(row)
            self.rows_removed.emit(deleted_images)

            offset += r.rowCount()

    def create_row(self) -> int:
        row = self.rowCount()
        self.insertRow(row)
        return row

    def fill_row(self, image: ImageViewModel, row: int) -> None:
        self.setItem(row, 0, ImageTitleTableWidget(image))
        self.setItem(row, 1, NormalTableWidgetItem(image))
        self.setItem(row, 2, PneumoniaTableWidgetItem(image))

    def add_image(self, image: ImageViewModel) -> None:
        row = self.create_row()
        self.fill_row(image, row)

    def on_cell_double_clicked(self, row: int, column: int) -> None:
        item = self.item(row, 0)
        assert isinstance(item, ImageTitleTableWidget)

        image_vm = item.image_vm
        image_widget = ImageDialog(image_vm)
        image_widget.exec()

    def dump(self) -> Tuple[List[str], List[Dict[str, str]]]:
        header = ["Название", "Пневмония", "Норма"]
        rows = []

        for i_row in range(self.rowCount()):
            row = {
                "Название": self.item(i_row, 0).text(),
                "Пневмония": self.item(i_row, 1).text(),
                "Норма": self.item(i_row, 2).text(),
            }
            rows.append(row)

        return header, rows
