# coding: utf-8

from PyQt5.QtWidgets import QWidget, QMessageBox


def _create_message(parent: QWidget, icon, window_title) -> QMessageBox:
    box = QMessageBox(parent)
    box.setIcon(icon)
    box.setWindowTitle(window_title)
    return box


def get_error_message(parent: QWidget) -> QMessageBox:
    message = _create_message(parent, QMessageBox.Warning, "Ошибка")
    return message


def get_success_message(parent: QWidget) -> QMessageBox:
    message = _create_message(parent, QMessageBox.Information, "Успех")
    return message


def show_error_dialog(parent: QWidget, text: str) -> None:
    box = get_error_message(parent)
    box.setText(text)
    box.exec()


def show_success_dialog(parent: QWidget, text: str) -> None:
    box = get_success_message(parent)
    box.setText(text)
    box.exec()
