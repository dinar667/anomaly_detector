# coding: utf-8

# ----
# Внимание! 
# Этот плагин был сгенерирован автоматически.
# Любые изменения в нем могут быть потеряны!

from PyQt5.QtGui import QIcon
from PyQt5.QtDesigner import QPyDesignerCustomWidgetPlugin

from gui.widgets.image_dialog import ImageDialog


class ImageDialogPlugin(QPyDesignerCustomWidgetPlugin):

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
        return ImageDialog(parent)

    def name(self):
        return "ImageDialog"

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
        return '<widget class="ImageDialog" name="imageDialog">\n' \
               '</widget>\n'

    def includeFile(self):
        return "gui.widgets.image_dialog"

