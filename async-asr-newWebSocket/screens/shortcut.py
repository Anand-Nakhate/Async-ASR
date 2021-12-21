from PyQt5 import QtCore, QtGui, QtWidgets
from .customeditor_2 import EditorDelegate
from PyQt5.QtCore import pyqtSignal as Signal
import configparser

class Ui_Help(QtWidgets.QMainWindow):
    ChangeHotKey = Signal(str)

    def setupUi(self,updateHotKeySignal):
        self.ChangeHotKey.connect(self.updateHotKey)
        self.updateHotKeySignal = updateHotKeySignal
        self.config = configparser.ConfigParser()
        self.config.read('hotkey.ini')
        
        self.setObjectName("Help")
        self.resize(482, 600)
        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.shortcut_label = QtWidgets.QLabel(self.centralwidget)
        self.shortcut_label.setObjectName("shortcut_label")
        self.verticalLayout.addWidget(
            self.shortcut_label, 0, QtCore.Qt.AlignHCenter)
        self.shortcut_table = QtWidgets.QTableWidget(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.shortcut_table.sizePolicy().hasHeightForWidth())
        self.shortcut_table.setSizePolicy(sizePolicy)
        self.shortcut_table.setMinimumSize(QtCore.QSize(412, 0))
        self.shortcut_table.setBaseSize(QtCore.QSize(0, 0))
        self.shortcut_table.setAlternatingRowColors(True)
        self.shortcut_table.setSelectionMode(
            QtWidgets.QAbstractItemView.NoSelection)
        self.shortcut_table.setSelectionBehavior(
            QtWidgets.QAbstractItemView.SelectRows)
        self.shortcut_table.setShowGrid(True)
        self.shortcut_table.setObjectName("shortcut_table")
        self.shortcut_table.setColumnCount(2)
        self.shortcut_table.setItemDelegateForColumn(1, EditorDelegate(self))
        self.shortcut_table.setRowCount(12)
        self.shortcut_table.horizontalHeader().setSectionResizeMode(
            0, QtWidgets.QHeaderView.Stretch)
        self.shortcut_table.horizontalHeader().setSectionResizeMode(
            1, QtWidgets.QHeaderView.ResizeToContents)

        item = QtWidgets.QTableWidgetItem()
        font = QtGui.QFont()
        font.setPointSize(14)
        item.setFont(font)
        self.shortcut_table.setVerticalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.shortcut_table.setVerticalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.shortcut_table.setVerticalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.shortcut_table.setVerticalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        self.shortcut_table.setVerticalHeaderItem(4, item)
        item = QtWidgets.QTableWidgetItem()
        self.shortcut_table.setVerticalHeaderItem(5, item)
        item = QtWidgets.QTableWidgetItem()
        self.shortcut_table.setVerticalHeaderItem(6, item)
        item = QtWidgets.QTableWidgetItem()
        self.shortcut_table.setVerticalHeaderItem(7, item)
        item = QtWidgets.QTableWidgetItem()
        self.shortcut_table.setVerticalHeaderItem(8, item)
        item = QtWidgets.QTableWidgetItem()
        self.shortcut_table.setVerticalHeaderItem(9, item)
        item = QtWidgets.QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        item.setFont(font)
        self.shortcut_table.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        item.setFont(font)
        self.shortcut_table.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        font = QtGui.QFont()
        font.setPointSize(12)
        item.setFont(font)
        self.shortcut_table.setItem(0, 0, item)
        item = QtWidgets.QTableWidgetItem()
        font = QtGui.QFont()
        font.setPointSize(12)
        item.setFont(font)
        self.shortcut_table.setItem(0, 1, item)
        item = QtWidgets.QTableWidgetItem()
        font = QtGui.QFont()
        font.setPointSize(12)
        item.setFont(font)
        self.shortcut_table.setItem(1, 0, item)
        item = QtWidgets.QTableWidgetItem()
        font = QtGui.QFont()
        font.setPointSize(12)
        item.setFont(font)
        self.shortcut_table.setItem(1, 1, item)
        item = QtWidgets.QTableWidgetItem()
        font = QtGui.QFont()
        font.setPointSize(12)
        item.setFont(font)
        self.shortcut_table.setItem(2, 0, item)
        item = QtWidgets.QTableWidgetItem()
        font = QtGui.QFont()
        font.setPointSize(12)
        item.setFont(font)
        self.shortcut_table.setItem(2, 1, item)
        item = QtWidgets.QTableWidgetItem()
        font = QtGui.QFont()
        font.setPointSize(12)
        item.setFont(font)
        self.shortcut_table.setItem(3, 0, item)
        item = QtWidgets.QTableWidgetItem()
        font = QtGui.QFont()
        font.setPointSize(12)
        item.setFont(font)
        self.shortcut_table.setItem(3, 1, item)
        item = QtWidgets.QTableWidgetItem()
        font = QtGui.QFont()
        font.setPointSize(12)
        item.setFont(font)
        self.shortcut_table.setItem(4, 0, item)
        item = QtWidgets.QTableWidgetItem()
        font = QtGui.QFont()
        font.setPointSize(12)
        item.setFont(font)
        self.shortcut_table.setItem(4, 1, item)
        item = QtWidgets.QTableWidgetItem()
        font = QtGui.QFont()
        font.setPointSize(12)
        item.setFont(font)
        self.shortcut_table.setItem(5, 0, item)
        item = QtWidgets.QTableWidgetItem()
        font = QtGui.QFont()
        font.setPointSize(12)
        item.setFont(font)
        self.shortcut_table.setItem(5, 1, item)
        item = QtWidgets.QTableWidgetItem()
        font = QtGui.QFont()
        font.setPointSize(12)
        item.setFont(font)
        self.shortcut_table.setItem(6, 0, item)
        item = QtWidgets.QTableWidgetItem()
        font = QtGui.QFont()
        font.setPointSize(12)
        item.setFont(font)
        self.shortcut_table.setItem(6, 1, item)
        item = QtWidgets.QTableWidgetItem()
        font = QtGui.QFont()
        font.setPointSize(12)
        item.setFont(font)
        self.shortcut_table.setItem(7, 0, item)
        item = QtWidgets.QTableWidgetItem()
        font = QtGui.QFont()
        font.setPointSize(12)
        item.setFont(font)
        self.shortcut_table.setItem(7, 1, item)
        item = QtWidgets.QTableWidgetItem()
        font = QtGui.QFont()
        font.setPointSize(12)
        item.setFont(font)
        self.shortcut_table.setItem(8, 0, item)
        item = QtWidgets.QTableWidgetItem()
        font = QtGui.QFont()
        font.setPointSize(12)
        item.setFont(font)
        self.shortcut_table.setItem(8, 1, item)
        item = QtWidgets.QTableWidgetItem()
        font = QtGui.QFont()
        font.setPointSize(12)
        item.setFont(font)
        self.shortcut_table.setItem(9, 0, item)
        item = QtWidgets.QTableWidgetItem()
        font = QtGui.QFont()
        font.setPointSize(12)
        item.setFont(font)
        self.shortcut_table.setItem(9, 1, item)
        item = QtWidgets.QTableWidgetItem()
        font = QtGui.QFont()
        font.setPointSize(12)
        item.setFont(font)
        self.shortcut_table.setItem(10, 0, item)
        item = QtWidgets.QTableWidgetItem()
        font = QtGui.QFont()
        font.setPointSize(12)
        item.setFont(font)
        self.shortcut_table.setItem(10, 1, item)
        item = QtWidgets.QTableWidgetItem()
        font = QtGui.QFont()
        font.setPointSize(12)
        item.setFont(font)
        self.shortcut_table.setItem(10, 0, item)
        item = QtWidgets.QTableWidgetItem()
        font = QtGui.QFont()
        font.setPointSize(12)
        item.setFont(font)
        self.shortcut_table.setItem(10, 1, item)
        item = QtWidgets.QTableWidgetItem()
        font = QtGui.QFont()
        font.setPointSize(12)
        item.setFont(font)
        self.shortcut_table.setItem(11, 0, item)
        item = QtWidgets.QTableWidgetItem()
        font = QtGui.QFont()
        font.setPointSize(12)
        item.setFont(font)
        self.shortcut_table.setItem(11, 1, item)
        item = QtWidgets.QTableWidgetItem()
        font = QtGui.QFont()
        font.setPointSize(12)
        item.setFont(font)
        self.shortcut_table.setItem(12, 0, item)
        item = QtWidgets.QTableWidgetItem()
        font = QtGui.QFont()
        font.setPointSize(12)
        item.setFont(font)
        self.shortcut_table.setItem(12, 1, item)
        item = QtWidgets.QTableWidgetItem()
        font = QtGui.QFont()
        font.setPointSize(12)
        item.setFont(font)
        self.shortcut_table.horizontalHeader().setDefaultSectionSize(205)
        self.shortcut_table.verticalHeader().setVisible(False)
        self.verticalLayout.addWidget(
            self.shortcut_table, 0, QtCore.Qt.AlignHCenter)
        self.setCentralWidget(self.centralwidget)

        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("Help", "MainWindow"))
        self.shortcut_label.setText(_translate("Help", "Keyboard Shortcuts"))
        item = self.shortcut_table.verticalHeaderItem(0)
        item.setText(_translate("Help", "1"))
        item = self.shortcut_table.verticalHeaderItem(1)
        item.setText(_translate("Help", "2"))
        item = self.shortcut_table.verticalHeaderItem(2)
        item.setText(_translate("Help", "3"))
        item = self.shortcut_table.verticalHeaderItem(3)
        item.setText(_translate("Help", "4"))
        item = self.shortcut_table.verticalHeaderItem(4)
        item.setText(_translate("Help", "5"))
        item = self.shortcut_table.verticalHeaderItem(5)
        item.setText(_translate("Help", "6"))
        item = self.shortcut_table.verticalHeaderItem(6)
        item.setText(_translate("Help", "7"))
        item = self.shortcut_table.verticalHeaderItem(7)
        item.setText(_translate("Help", "8"))
        item = self.shortcut_table.horizontalHeaderItem(0)
        item.setText(_translate("Help", "Action"))
        item = self.shortcut_table.horizontalHeaderItem(1)
        item.setText(_translate("Help", "Shortcut Key"))
        __sortingEnabled = self.shortcut_table.isSortingEnabled()
        self.shortcut_table.setSortingEnabled(False)
        
        item = self.shortcut_table.item(0, 0)
        item.setText(_translate("Help", "Play/Pause Audio Message"))
        
        item = self.shortcut_table.item(0, 1)
        item.setText(_translate("Help", self.config["HOTKEY"]["play"]))
        item.setData(QtCore.Qt.UserRole,"play") 
        
        item = self.shortcut_table.item(1, 0)
        item.setText(_translate("Help", "Restart audio playback"))
        
        item = self.shortcut_table.item(1, 1)
        item.setText(_translate("Help", self.config["HOTKEY"]["restartplay"]))
        item.setData(QtCore.Qt.UserRole,"restartplay") 
        
        item = self.shortcut_table.item(2, 0)
        item.setText(_translate("Help", "Decrease playback speed"))
        
        item = self.shortcut_table.item(2, 1)
        item.setText(_translate("Help", self.config["HOTKEY"]["decreaseplayrate"]))
        item.setData(QtCore.Qt.UserRole,"decreaseplayrate") 
        
        item = self.shortcut_table.item(3, 0)
        item.setText(_translate("Help", "Increase playback speed"))
        
        item = self.shortcut_table.item(3, 1)
        item.setText(_translate("Help", self.config["HOTKEY"]["increaseplayrate"]))
        item.setData(QtCore.Qt.UserRole,"increaseplayrate") 
        
        item = self.shortcut_table.item(4, 0)
        item.setText(_translate("Help", "Reset playback speed"))
        
        item = self.shortcut_table.item(4, 1)
        item.setText(_translate("Help", self.config["HOTKEY"]["resetplayrate"]))
        item.setData(QtCore.Qt.UserRole,"resetplayrate") 
        
        item = self.shortcut_table.item(5, 0)
        item.setText(_translate("Help", "Toggle auto loop playback"))
        
        item = self.shortcut_table.item(5, 1)
        item.setText(_translate("Help", self.config["HOTKEY"]["autoloop"]))
        item.setData(QtCore.Qt.UserRole,"autoloop")
        
        item = self.shortcut_table.item(6, 0)
        item.setText(_translate("Help", "Enter or Save edit mode"))
        
        item = self.shortcut_table.item(6, 1)
        item.setText(_translate("Help", "Enter"))
        item.setData(QtCore.Qt.UserRole,"EnterexitEdit") 
        item.setFlags(QtCore.Qt.ItemIsEditable)
        # item = self.shortcut_table.item(3, 0)
        # item.setText(_translate("Help", "Save and exit edit mode"))
        
        # item = self.shortcut_table.item(3, 1)
        # item.setText(_translate("Help", "Ctrl+enter"))
        
        item = self.shortcut_table.item(7, 0)
        item.setText(_translate("Help", "Discard and exit edit mode"))
        
        item = self.shortcut_table.item(7, 1)
        item.setText(_translate("Help", "Esc"))
        item.setData(QtCore.Qt.UserRole,"exitEdit") 
        item.setFlags(QtCore.Qt.ItemIsEditable)
        
        item = self.shortcut_table.item(8, 0)
        item.setText(_translate("Help", "Delete transcript row"))
        
        item = self.shortcut_table.item(8, 1)
        item.setText(_translate("Help", "Delete"))
        item.setData(QtCore.Qt.UserRole,"delete") 
        item.setFlags(QtCore.Qt.ItemIsEditable)
        
        item = self.shortcut_table.item(9, 0)
        item.setText(_translate("Help", "Search for a Page"))
        
        item = self.shortcut_table.item(9, 1)
        item.setText(_translate("Help", self.config["HOTKEY"]["searchpage"]))
        item.setData(QtCore.Qt.UserRole,"searchpage") 
        
        item = self.shortcut_table.item(10, 0)
        item.setText(_translate("Help", "Start a new session"))
        
        item = self.shortcut_table.item(10, 1)
        item.setText(_translate("Help", self.config["HOTKEY"]["newsession"]))
        item.setData(QtCore.Qt.UserRole,"newsession") 
        
        item = self.shortcut_table.item(11, 0)
        item.setText(_translate("Help", "Open shorcut window"))
        
        item = self.shortcut_table.item(11, 1)
        item.setText(_translate("Help", self.config["HOTKEY"]["help"]))
        item.setData(QtCore.Qt.UserRole,"help")
        
        self.shortcut_table.setSortingEnabled(__sortingEnabled)

    def updateHotKey(self,hotkey):
        self.updateHotKeySignal.emit(self.shortcut_table.currentItem().data(QtCore.Qt.UserRole),hotkey)