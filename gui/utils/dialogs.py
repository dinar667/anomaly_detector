# coding: utf-8

from PyQt5.QtWidgets import QWidget, QMessageBox


def get_error_message(parent: QWidget) -> QMessageBox:
    box = QMessageBox(parent)
    box.setIcon(QMessageBox.Warning)
    box.setWindowTitle("Ошибка")
    return box


def show_error_dialog(parent: QWidget, text: str) -> None:
    box = get_error_message(parent)
    box.setText(text)
    box.exec()
