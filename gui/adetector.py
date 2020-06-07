# coding: utf-8

import sys

from PyQt5.QtWidgets import QApplication
from dataclasses import dataclass

from gui.widgets.main_window import MainWindow


@dataclass(frozen=True)
class PDetector:
    main_window: MainWindow

    def run(self) -> None:
        self.main_window.show()


def main() -> None:
    app = QApplication(sys.argv)

    main_window = MainWindow()
    pdetector = PDetector(main_window)
    pdetector.run()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
