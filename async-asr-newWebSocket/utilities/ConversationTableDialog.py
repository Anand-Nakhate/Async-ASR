from PyQt5 import QtCore, QtWidgets
#from utilities.CustomTableWidget1 import CustomTableWidget1
from screens.customeditor import EditorDelegate

shared_FullData = {}

class ConversationTableDialog(QtWidgets.QDialog):

    def __init__(self, rows_required, FullData, pageData, pageLimit, pageLimitList, page, customsignal, parent=None):

        super(ConversationTableDialog, self).__init__(parent)
        self.rows_required = rows_required
        self.FullData = FullData
        self.pageData = pageData
        self.pageLimit = pageLimit
        self.pageLimitList = pageLimitList
        self.page = page
        self.customsignal = customsignal
        self.setWindowFlags(QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowTitleHint)
        self.title = "ASR - Analysis Conversation Table"
        self.setWindowTitle(self.title)
        self.setModal(True)

        self.horizontalLayout = QtWidgets.QHBoxLayout(self)
        self.horizontalLayout.setObjectName("horizontalLayout")

        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")

        #Setup Custom Table Widget
        self.conversation_table = CustomTableWidget1(self.rows_required)
        #self.conversation_table.FullData = self.FullData
        self.conversation_table.pageData = self.pageData
        self.conversation_table.pageLimit = self.pageLimit
        self.conversation_table.pageLimitList = self.pageLimitList
        self.conversation_table.page = self.page

        self.conversation_table.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.conversation_table.customContextMenuRequested.connect(self.generateMenu)
        self.conversation_table.viewport().installEventFilter(self)
        #self.conversation_table = QtWidgets.QTableWidget(self)
        # self.conversation_table.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.conversation_table.sizePolicy().hasHeightForWidth())
        self.conversation_table.setSizePolicy(sizePolicy)
        self.conversation_table.setObjectName("conversation_table")
        self.conversation_table.setColumnCount(5)
        item = QtWidgets.QTableWidgetItem()
        item.setText("Speakers")
        self.conversation_table.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        item.setText("TimeStamp")
        self.conversation_table.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        item.setText("Messages")
        self.conversation_table.setHorizontalHeaderItem(2, item)
        self.conversation_table.setIconSize(QtCore.QSize(32, 32))
        self.conversation_table.horizontalHeader().setVisible(False)
        self.conversation_table.horizontalHeader().setDefaultSectionSize(18)
        self.conversation_table.horizontalHeader().setMinimumSectionSize(18)
        self.conversation_table.horizontalHeader().setStretchLastSection(True)
        self.conversation_table.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        self.conversation_table.verticalHeader().setVisible(False)
        self.conversation_table.verticalHeader().setStretchLastSection(False)
        self.conversation_table.verticalHeader().setDefaultSectionSize(40)
        self.conversation_table.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        self.conversation_table.setWordWrap(True)
        self.conversation_table.resizeRowsToContents()
        # self.conversation_table.setSelectionMode(
        # QtWidgets.QAbstractItemView.SingleSelection)
        self.conversation_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        
        self.conversation_table.setItemDelegateForColumn(2, EditorDelegate(self, self.customsignal))
        self.verticalLayout.addWidget(self.conversation_table)

        __sortingEnabled = self.conversation_table.isSortingEnabled()
        self.conversation_table.setSortingEnabled(False)
        self.conversation_table.setSortingEnabled(__sortingEnabled)
        self.conversation_table.hideColumn(4)
        self.conversation_table.hideColumn(3)

        self.button_layout = QtWidgets.QHBoxLayout()
        self.button_layout.setAlignment(QtCore.Qt.AlignCenter)
        self.button_layout.setObjectName("button_layout")

        self.cancelButton = QtWidgets.QPushButton('Cancel')
        self.button_layout.addWidget(self.cancelButton)

        self.verticalLayout.addLayout(self.button_layout)
        self.horizontalLayout.addLayout(self.verticalLayout)
        self.cancelButton.clicked.connect(self.reject)
        self.conversation_table.switchPage(self.page)

    def generateMenu(self, pos):
        print("pos======",pos)
        self.menu.exec_(self.conversation_table.mapToGlobal(pos))   #
