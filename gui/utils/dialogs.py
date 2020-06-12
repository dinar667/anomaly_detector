# coding: utf-8

from PyQt5.QtWidgets import QWidget, QMessageBox


def get_error_message(parent: QWidget) -> QMessageBox:
    box = QMessageBox(parent)
    box.setIcon(QMessageBox.Warning)
    box.setWindowTitle("Ошибка")
    return box


def get_success_message(parent: QWidget) -> QMessageBox:
    box = QMessageBox(parent)
    box.setIcon(QMessageBox.Information)
    box.setWindowTitle("Успех")
    return box


def show_error_dialog(parent: QWidget, text: str) -> None:
    box = get_error_message(parent)
    box.setText(text)
    box.exec()


def show_success_dialog(parent: QWidget, text: str) -> None:
    box = get_success_message(parent)
    box.setText(text)
    box.exec()
