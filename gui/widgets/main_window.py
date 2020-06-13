# coding: utf-8

from PyQt5.QtWidgets import QMainWindow

from gui.generated.ui_main_window import Ui_MainWindow
from gui.widgets.about_dialog import AboutDialog


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.setupUi(self)

    def on_about_required(self) -> None:
        dialog = AboutDialog(self)
        dialog.exec()
