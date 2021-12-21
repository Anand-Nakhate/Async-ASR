from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QTimer, QThread
from PyQt5.QtCore import pyqtSignal as SIGNAL
from PyQt5.QtGui import QBrush, QColor, QKeySequence


class CustomTreeWidgetItem(QtWidgets.QTreeWidgetItem):
    def __init__(self, parent=None, customsignal=None, ref=None):
        self.ref = ref
        self.customsignal = customsignal
        super(CustomTreeWidgetItem, self).__init__(parent)

    def setData(self, column, role, value):
        if role == 2:
            old_speaker = self.text(1)
            if self.ref is not None:
                old_speaker = self.text(0)
            new_speaker = value
            item_row = self.treeWidget().indexOfTopLevelItem(self)
            if old_speaker != new_speaker:
                self.customsignal.update_speakers.emit(
                    old_speaker, new_speaker, item_row)
        super(CustomTreeWidgetItem, self).setData(column, role, value)
