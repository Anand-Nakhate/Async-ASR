from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import pyqtSlot
import en_core_web_sm


class NER_TableDialog(QtWidgets.QDialog):
    def __init__(self, pageData,  parent=None):
        self.pageData = pageData
        super(NER_TableDialog, self).__init__(parent)
        self.setWindowFlags(QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowTitleHint)

        self.title = "ASR - Analysis NER Table"
        self.setWindowTitle(self.title)
        self.setModal(True)

        self.verticalLayout = QtWidgets.QVBoxLayout(self)
        self.verticalLayout.setObjectName("verticalLayout")

        self.createTable()
        self.verticalLayout.addWidget(self.tableWidget)


    def createTable(self):
       # Create table
        nlp = en_core_web_sm.load()
        #Collect all the row numbers of the oage
        keys = []
        for key in self.pageData:
            keys.append(key)
        # Calculate the number of named entities to get the row count of the table
        row_count = 0
        all_named_entities = {}
        for key in self.pageData:
            doc = nlp(self.pageData[key][1])
            for entry in doc.ents:
                all_named_entities[entry.text] = entry.label_
        row_count = len(all_named_entities)

        self.tableWidget = QtWidgets.QTableWidget()
        self.tableWidget.setRowCount(row_count)
        self.tableWidget.setColumnCount(3)
        labels = ["Time Stamp", "Item", "Named Entity"]
        self.tableWidget.setHorizontalHeaderLabels(labels)
        header = self.tableWidget.horizontalHeader()       
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
        #Fill data in the table
        table_entry_number = 0
        for row in range(len(self.pageData)):
            named_entities = {}
            doc = nlp(self.pageData[keys[row]][1])
            for entry in doc.ents:
                named_entities[entry.text] = entry.label_
            for key in named_entities:
                self.tableWidget.setItem(table_entry_number, 0, QtWidgets.QTableWidgetItem(self.pageData[keys[row]][0]))
                self.tableWidget.setItem(table_entry_number, 1, QtWidgets.QTableWidgetItem(key))
                self.tableWidget.setItem(table_entry_number, 2, QtWidgets.QTableWidgetItem(named_entities[key]))
                table_entry_number = table_entry_number + 1

        
        # self.tableWidget.move(0,0)

        # table selection change
        self.tableWidget.doubleClicked.connect(self.on_click)
    
    @pyqtSlot()
    def on_click(self):
        print("\n")
        for currentQTableWidgetItem in self.tableWidget.selectedItems():
            print(currentQTableWidgetItem.row(), currentQTableWidgetItem.column(), currentQTableWidgetItem.text())

