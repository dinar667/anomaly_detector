# coding: utf-8

from PyQt5.QtWidgets import QMainWindow

from gui.generated.ui_main_window import Ui_MainWindow


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.setupUi(self)
