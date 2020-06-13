# coding: utf-8

from PyQt5.QtWidgets import QDialog

from gui.generated.ui_about_dialog import Ui_AboutDialog


class AboutDialog(QDialog, Ui_AboutDialog):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.setupUi(self)
