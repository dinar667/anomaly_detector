# coding: utf-8

# ----
# Внимание! 
# Этот плагин был сгенерирован автоматически.
# Любые изменения в нем могут быть потеряны!

from PyQt5.QtGui import QIcon
from PyQt5.QtDesigner import QPyDesignerCustomWidgetPlugin

from gui.widgets.main_window import MainWindow


class MainWindowPlugin(QPyDesignerCustomWidgetPlugin):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.initialized = False

    def initialize(self, core):
        if self.initialized:
            return

        self.initialized = True

    def isInitialized(self):
        return self.initialized

    def createWidget(self, parent):
        return MainWindow(parent)

    def name(self):
        return "MainWindow"

    def group(self):
        return "Custom Widgets"

    def icon(self):
        return QIcon()

    def toolTip(self):
        return ""

    def whatsThis(self):
        return ""

    def isContainer(self):
        return False

    def domXml(self):
        return '<widget class="MainWindow" name="mainWindow">\n' \
               '</widget>\n'

    def includeFile(self):
        return "gui.widgets.main_window"

