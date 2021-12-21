import en_core_web_sm
nlp = en_core_web_sm.load()
doc = nlp("This is a Apple. Hello New York Washington.")
print([(w.text, w.label_) for w in doc.ents])


import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QAction, QTableWidget,QTableWidgetItem,QVBoxLayout
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot


def NER_module_table_handler(self):
    global shared_FullData
    shared_FullData = self.conversation_table.FullData
    lower_page_limit, upper_page_limit = self.conversation_table.getLimits()
    pageData = {}
    for rowID in range(lower_page_limit, upper_page_limit+1):
            if rowID in shared_FullData:
                pageData[rowID] = []
                idx = 0
                for element in shared_FullData[rowID]:
                    if isinstance(element, QtWidgets.QTableWidgetItem):
                        if(idx == 3 or idx == 4):
                            pageData[rowID].append(element.text())
                    idx = idx+1

    ner_table_dialog = NER_TableDialog()
    

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

        self.tableWidget = QTableWidget()
        self.tableWidget.setRowCount(row_count)
        self.tableWidget.setColumnCount(3)
        labels = ["Time Stamp", "Item", "Named Entity"]
        self.tableWidget.setHorizontalHeaderLabels(labels)
        #Fill data in the table
        table_entry_number = 0
        for row in range(len(self.pageData)):
            named_entities = {}
            doc = nlp(self.pageData[keys[row][1]])
            for entry in doc.ents:
                named_entities[entry.text] = entry.label_
            for key in named_entities:
                self.tableWidget.setItem(table_entry_number, 0, QTableWidgetItem(self.pageData[keys[row]][0]))
                self.tableWidget.setItem(table_entry_number, 1, QTableWidgetItem(key))
                self.tableWidget.setItem(table_entry_number, 2, QTableWidgetItem(named_entities[key]))
                table_entry_number = table_entry_number + 1

        
        # self.tableWidget.move(0,0)

        # table selection change
        self.tableWidget.doubleClicked.connect(self.on_click)
    
    @pyqtSlot()
    def on_click(self):
        print("\n")
        for currentQTableWidgetItem in self.tableWidget.selectedItems():
            print(currentQTableWidgetItem.row(), currentQTableWidgetItem.column(), currentQTableWidgetItem.text())





class App(QWidget):

    def __init__(self):
        super().__init__()
        self.title = 'PyQt5 table - pythonspot.com'
        self.left = 0
        self.top = 0
        self.width = 300
        self.height = 200
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        
        self.createTable()

        # Add box layout, add table to box layout and add box layout to widget
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.tableWidget) 
        self.setLayout(self.layout) 

        # Show widget
        self.show()

    def createTable(self):
       # Create table
        self.tableWidget = QTableWidget()
        self.tableWidget.setRowCount(4)
        self.tableWidget.setColumnCount(2)
        labels = ["Item", "Named Entity"]
        self.tableWidget.setHorizontalHeaderLabels(labels)
        self.tableWidget.setItem(0,0, QTableWidgetItem("Cell (1,1)"))
        self.tableWidget.setItem(0,1, QTableWidgetItem("Cell (1,2)"))
        self.tableWidget.setItem(1,0, QTableWidgetItem("Cell (2,1)"))
        self.tableWidget.setItem(1,1, QTableWidgetItem("Cell (2,2)"))
        self.tableWidget.setItem(2,0, QTableWidgetItem("Cell (3,1)"))
        self.tableWidget.setItem(2,1, QTableWidgetItem("Cell (3,2)"))
        self.tableWidget.setItem(3,0, QTableWidgetItem("Cell (4,1)"))
        self.tableWidget.setItem(3,1, QTableWidgetItem("Cell (4,2)"))
        self.tableWidget.move(0,0)

        # table selection change
        self.tableWidget.doubleClicked.connect(self.on_click)

    @pyqtSlot()
    def on_click(self):
        print("\n")
        for currentQTableWidgetItem in self.tableWidget.selectedItems():
            print(currentQTableWidgetItem.row(), currentQTableWidgetItem.column(), currentQTableWidgetItem.text())
 
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_()) 