import sys
sys.path.append('../')
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import QtCore, QtGui, QtWidgets
from screens.customeditor import EditorDelegate
import copy 

class CustomTableWidget(QtWidgets.QTableWidget):
    """A custom table class which inherit from QTableWidget that supports pagination
    """
    def __init__(self):
        """Inits CustomTableWidget.
 
        Attributes:
            FullData (dict:<RowIndex,RowData>): It hold the full data of the table
            pageData (list:[<RowIndex,dirtyBit,col1Data,,col2Data,,col3Data...>]): Currently displayed page data
            pageLimit (int): The page limit. (Default = 10). This value can be change for different page limit size
            pageLimitList (dict:<PageNumber,UpperLimit>): This dictionary hold the page limit for each page which
                can be accessed using page number as KEY. This will support dynamic page limit for each page
            page (int): The current page number
            pageListWidget (QtWidgets): 
            autoSwitchPage (Boolean): Boolean to determine when to switch page automatically.
            ListItemCount (int):
            listitemsize (int): The size used to draw the page number list (Default = 45)
            bool (Boolean): Prevent the class from redrawing table view using setAutoSwitchPage(bool). Set to false
                when loading the table for the first time for better performance. Set to true data is fully loaded
            bookmarksList (list:<RowIndex>): It contain the bookmarked rowIndex, used to redraw bookmark indicator after
                the pagelimit change
        """
        super().__init__()
        self.FullData = {}
        self.pageData = []
        self.pageLimit = 10
        self.pageLimitList = {}
        self.pageLimitList[1] = self.pageLimit - 1
        self.page = 1
        self.pageListWidget = None
        self.autoSwitchPage =  False
        self.ListItemCount = 0
        # self._flag = False
        self.listitemsize = 45
        self.bool = True
        self.bookmarksList = [] 

    # Right Click function
    def createBookMark(self,rowID):
        """Method to create a bookmark
        
        The rowID will be appended to self.bookmarksList
        
        Args:
            rowID (int): The row index to be added as bookmark

        """
        s = set(self.bookmarksList)
        if self.currentRow() not in s:
            self.bookmarksList.append(self.currentRow())
        self.redrawList(self.page)
        print("Added to bookmarks")
        
    def splitPage(self,index):
        """Method to split a single page into 2
        
        Args:
            index (int): The row index in a page to start spliting into 2 page

        """
        # If current page only have 1 row, return.
        if len(self.pageData) == 1:
            return
        
        self.duplicate()
        totalRow = len(self.FullData)
        firstHalf = index
        oldvalue = 0
        # If next page already has data we need to shift self.pageLimitList value back and append the new data.
        # else directly apeend the new page
        if self.page+1 in self.pageLimitList:
            tempPage = self.page + 1
            counter = 0
            while tempPage in self.pageLimitList:
                if counter == 0:
                    nextValue = self.pageLimitList[tempPage]
                    oldvalue = nextValue
                    currentValue = self.pageLimitList[tempPage-1]
                    self.pageLimitList[tempPage] = currentValue
                else:
                    oldvalue = nextValue
                    nextValue = self.pageLimitList[tempPage]
                    self.pageLimitList[tempPage] = oldvalue
                tempPage = tempPage + 1
                counter = counter + 1
            self.pageLimitList[tempPage] = oldvalue + self.pageLimit
        else:
            self.pageLimitList[self.page+1] = firstHalf + self.pageLimit
        self.pageLimitList[self.page] = firstHalf
        self.page = self.page + 1
        self.pageData = self.getPageSlice()
        self.setRowCount(0)
        self.buildPage()
        self.addNewPageItem()
        
    ## general function
    def getMaxItem(self):
        """Calculate the number of item that can be drawn in the QListWidget
        
        Calculated using QListWidget width / self.listitemsize
        
        Returns:
            maxItem (int): number of item that can be drawn

        """
        width = self.pageListWidget.frameGeometry().width()
        maxItem = int(width/self.listitemsize)
        return maxItem        
    
   
    def switchPage(self,pageID):
        """Switch the table to a specific page number
        
        Args:
            pageID (int): Page number

        """
        if(pageID > len(self.pageLimitList)): return
        # self.pageData = self.getPageSlice()
        self.duplicate()
        self.page = pageID
        self.pageData = self.getPageSlice()
        self.setRowCount(0)
        print("Page : " + str(self.page))
        self.buildPage()
        self.redrawList(pageID)

    def changePageLimit(self,pagelimit):
        """Change the number of entries show by the table
        
        Click on the dropdown list in the GUI to change the number of entries
        
        Args:
            pagelimit (int): Number of entries(row) to show per page

        """
        newpageLimitList = {}
        pagelimit = int(pagelimit)
        
        # Recalculate the number of page which is total row / number of entries per page
        totalrow = self.rowCount()
        loop = totalrow//pagelimit + 1
        for i in range(loop):
            newpageLimitList[i+1] = (pagelimit)*(i+1) -1
        self.duplicate()
        self.pageLimitList=newpageLimitList
        self.pageLimit = pagelimit
        self.ListItemCount = loop
        self.page = 1
        self.switchPage(1)
        self.redrawList(1)
        # self.bookmarksList = []
            
    def duplicate(self):
        """Duplicate the data in self.FullData 
        
        Whenever current page data change, self.setRowCount(0) is called to clear table content. 
        Therefore, items in self.FullData will be removed from the memory. Hence, we will create a new instance of
        QTableWidgetItem and copy the important feature needed such as text, data, color...etc.
        To improve performace, a dirty bit (self.FullData[key][1]) is set to prevent duplicating the whole full data.      
        
        """
        # Set current page dirty bit
        lp, up = self.getLimits2(self.page)
        for i in range(up-lp):
            if (lp+i+1) in self.FullData:
                self.FullData[lp+i+1][1] = True
            else:
                break
        for key in self.FullData:
            if(self.FullData[key][1]):
                rowData = self.FullData[key]
                self.FullData[key][0] = rowData[0]
                self.FullData[key][1] = False
                colIndex = 2
                for data in rowData:
                    if isinstance(data,QtWidgets.QTableWidgetItem):
                        dup = QtWidgets.QTableWidgetItem()
                        dup.setText(data.text())
                        dup.setData(QtCore.Qt.UserRole,data.data(QtCore.Qt.UserRole))
                        dup.setBackground(data.background())
                        dup.setFont(data.font())
                        dup.setIcon(data.icon())
                        self.FullData[key][colIndex] = dup
                        colIndex = colIndex + 1
                      
    def buildPage(self):
        """Function to build the page
        
        Data in self.pageData will be inserted into the table
        
        """
        counter = 0
        for data in self.pageData:
            super().insertRow(counter)
            item_count = 0
            for item in data:
                if isinstance(item,QtWidgets.QTableWidgetItem):
                    super().setItem(counter,item_count,item)
                    item_count = item_count + 1
            counter = counter + 1

    def nextPage(self):
        """Nagivage the table to the next page
        """
        if(self.page + 1) > len(self.pageLimitList) : return
        self.duplicate()
        self.page = self.page + 1
        self.pageData = self.getPageSlice()
        self.setRowCount(0)
        print("Page : " + str(self.page))
        self.buildPage()
        self.redrawList(self.page)
        pass
    
    def prevPage(self):
        """Nagivage the table to the previous page
        """
        if(self.page - 1) == 0: return
        self.duplicate()
        self.page = self.page - 1
        self.pageData = self.getPageSlice()
        self.setRowCount(0)
        print("Page : " + str(self.page))
        self.buildPage()
        self.redrawList(self.page)

    def getPageSlice(self):
        """Get the current page data information from self.fullData
        
        Returns:
            listData(List): Return current page data as a list
     
        """
        # dict_items = self.FullData.items()
        # pagesize = self.pageLimitList[self.page]
        lowerlimit,upperlimit = self.getLimits()
        listData = []
        for i in range((upperlimit+1)-(lowerlimit+1)):
            if i+lowerlimit+1 in self.FullData:
                listData.append(self.FullData[i+lowerlimit+1])
            else: break
        return listData
        # return list(dict_items)[lowerlimit+1:upperlimit+1]
             
    def setAutoSwitchPage(self, boolean):
        """Turn off Page switching to improve performance when loading the table for the first time
        
        Args:
            boolean (bool)
     
        """
        self.bool = boolean
        if self.bool:
            self.pageListWidget.model().rowsInserted.connect(self._recalcultate_height)
            self.pageListWidget.model().rowsRemoved.connect(self._recalcultate_height)
    
    def isPageFull(self):
        """Check if the current page is full
        
        Returns:
            True if current page is full, False otherwise.

        """
        pagesize = len(self.pageData)
        lowerlimit,upperlimit = self.getLimits()
        pagelimit = upperlimit - lowerlimit
        if pagesize >=  pagelimit:
            return True
        return False
    
    def getLimits2(self,pageID):
        """Get the page limit boundary  
        
        Args:
            pageID (int): Page number
        
        Returns:
            lowerlimit (int): Lower boundary of the page limit
            upperlimit (int): Higher boundary of the page limit

        """
        if pageID-1 == 0:
            lowerlimit = -1
        else:
            lowerlimit = self.pageLimitList[pageID-1]
        if(pageID) in self.pageLimitList: 
            upperlimit = self.pageLimitList[pageID]
        else:
            upperlimit = lowerlimit + self.pageLimit
        return lowerlimit,upperlimit
    
    def getLimits(self):
        """Get the current page limit boundary  
        
        Returns:
            lowerlimit (int): Lower boundary of the page limit
            upperlimit (int): Higher boundary of the page limit

        """
        if self.page-1 == 0:
            lowerlimit = -1
        else:
            lowerlimit = self.pageLimitList[self.page-1]
        if(self.page) in self.pageLimitList: 
            upperlimit = self.pageLimitList[self.page]
        else:
            upperlimit = len(self.FullData)
        return lowerlimit,upperlimit
        
    
    
    ## List view functions ## 
    def redrawList(self,selectedPage):     
        """Re-draw the QlistWidget whenever the page changes

        Args:
            selectedPage (int): The current page

        """                  
        width = self.pageListWidget.frameGeometry().width()
        maxItem = int(width/self.listitemsize)
        half = maxItem/2
        if maxItem%2 ==0:    
            offset = int(selectedPage-half)+1
        else:
            offset =  int(selectedPage-half)+1
            half = half-0.5
        if offset <=0:
            offset=1
        if selectedPage + half >= self.ListItemCount :
            offset = self.ListItemCount - maxItem + 1
        self.pageListWidget.model().rowsInserted.disconnect()
        self.pageListWidget.model().rowsRemoved.disconnect() 
        self.pageListWidget.clear()
        for i in range(maxItem):
            if i+offset <=0:
                continue
            if i+offset > self.ListItemCount:
                continue
            item1 = QtWidgets.QListWidgetItem(str(i+offset))
            item1.setData(Qt.UserRole,i+offset)
            item1.setTextAlignment(Qt.AlignCenter)
            item1.setSizeHint(QSize (self.listitemsize,1))
            self.pageListWidget.addItem(item1) 
            
        self.pageListWidget.model().rowsInserted.connect(self._recalcultate_height)
        self.pageListWidget.model().rowsRemoved.connect(self._recalcultate_height)
        # s = set(self.bookmarksList)
        tempPageData = []

        for bmItem in self.bookmarksList:
            for item in self.pageLimitList:
                pageItem = self.pageLimitList[item]
                if bmItem <= pageItem:
                    tempPageData.append(item)
                    break;
            
        s = set(tempPageData)
        for i in range(self.pageListWidget.count()):
            item = self.pageListWidget.item(i)
            if str(int(item.text()))==str(selectedPage):
                f = item.font()
                f.setBold(True)
                item.setFont(f)
            if int(item.text()) in s:
                fg = item.foreground().color()
                fg.setRed(255)
                item.setForeground(fg)
                
    def setpageListWidget(self, pageListWidget):
        self.pageListWidget = pageListWidget

    
    def addNewPageItem(self):
        """Add new page number to QlistWidget
        """  
        numOfItem = self.ListItemCount
        self.ListItemCount = self.ListItemCount + 1
        if self.bool:
            item1 = QtWidgets.QListWidgetItem(str(numOfItem+1) )
            item1.setData(Qt.UserRole,numOfItem+1)
            item1.setSizeHint(QSize (self.listitemsize,1))
            self.pageListWidget.addItem(item1) 
            self.pageListWidget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            self.pageListWidget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
    def _recalcultate_height(self):
        """Called whenever the window size change. QListWidget will be re-drawn to fit the size
        """  
        if self.bool:
            self.redrawList(self.page)
            
    def resizeEvent(self, event):
        """Called whenever the window size change. QListWidget will be re-drawn to fit the size
        """
        if self.bool:
            self.redrawList(self.page)
        super().resizeEvent(event)
    
    
    ## Table Function
    def setItem(self,index,col,item):
        """Override QTableWidget setItem
        
        Instead of directly insert into QTableWidget, it will check if the item added is within the page limit.
        If the item is within the pagelimit it will be displayed, otherwise stored in the self.fulldata
        
        Args:
            index (int): Row index
            col (int): Column index
            item (QTableWidgetItem): QTableWidgetItem to be added

        """   
        lowerlimit,upperlimit = self.getLimits2(self.page)
        if index > lowerlimit and index <= upperlimit:
            super().setItem(index-lowerlimit-1,col,item)
        if index in self.FullData:
            self.FullData[index][col+2] = item
            self.FullData[index][1] = True
        else:
            self.FullData[index] = [index,True,None,None,None,None,None,None]
            self.FullData[index][col+2] = item
        self.pageData = self.getPageSlice()
        if(self.autoSwitchPage):
            if self.bool == False: return
            if self.page != len(self.pageLimitList)-1: return
            
            self.switchPage(self.page+1)
            self.autoSwitchPage = False
        
    def insertRow(self,index):
        """Override QTableWidget insertRow
        
        Instead of directly insert a new row into QTableWidget, it will check if the row is within the page limit.
        If the row is within the pagelimit it will be added, otherwise it will automatically which to next page then 
        add the new row.
        
        Args:
            index (int): Row index

        """   
        if(index == 0):
            self.addNewPageItem() 
        if not self.isPageFull():
            super().insertRow(super().rowCount())
        else: ## current view page is full
            totalRow = len(self.FullData) - 1
            lowerlimit,upperlimit = self.getLimits2(len(self.pageLimitList))
            if(totalRow >= upperlimit):
                self.addNewPageItem() 
                self.pageLimitList[len(self.pageLimitList)+1] = upperlimit + self.pageLimit
                self.autoSwitchPage = True
                
    def item(self, row, col):
        """Retrieve the item at the table by row and column position
        
        Args:
            row (int): Row index
            col (int): Column index
            
        Returns:
            QTableWidgetItem (QtWidget)       

        """   
        return self.FullData[row][col+2]
    
    def currentRow(self):
        """Return the currently selected row index
        
        Return the row index directly from parent class if current page is 1, otherwise row index need to be calculated.
            As the parent class only return the row index relative to the displayed items.
            ``Example: Page limit = 10, Current Page 2, Selected 2nd row. The super().currentRow() will return 1 (2nd row)
            instead of 11 ()``
        
        Returns:
            dataCurrentRow (int): Selected row index

        """   
        pageCurrentRow = super().currentRow()
        if self.page-1 in self.pageLimitList:
            dataCurrentRow = self.pageLimitList[self.page-1] + pageCurrentRow + 1
        else:
            dataCurrentRow = pageCurrentRow
        return dataCurrentRow

    def rowCount(self):
        """Return total number of row
        
        Returns:
            len(self.FullData): Total number of row

        """   
        return len(self.FullData)


class MyWindow(QtWidgets.QWidget):
    """ A window used for debugging CustomTableWidget. Run CustomTable.py as main script for easlier debuging
    """
    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        
        self.c = 0
        # create table
        self.conversation_table = CustomTableWidget()
        
        self.conversation_table.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.conversation_table.customContextMenuRequested.connect(self.generateMenu)
        self.conversation_table.viewport().installEventFilter(self)
        
        self.createCustomTable()
        self.PageNumberList = QtWidgets.QListWidget()
        self.PageNumberList.viewport().setAutoFillBackground( False );

        self.PageNumberList.setFlow(QtWidgets.QListView.LeftToRight) 
        self.PageNumberList.setFixedHeight(40)
        self.PageNumberList.itemClicked.connect(self.ListItemClicked)
        self.conversation_table.setpageListWidget(self.PageNumberList)
        
        # layout
        self.layout = QtWidgets.QVBoxLayout()
        self.testButton = QtWidgets.QPushButton("Add Data")
        self.testButton.clicked.connect(self.test)        
        self.layout.addWidget(self.testButton)
        
        self.tb = QtWidgets.QPushButton("Test Color Code")
        self.tb.clicked.connect(self.test1)   
        self.layout.addWidget(self.tb)
        
        self.TopHlayout = QtWidgets.QHBoxLayout()
        self.showEntries = QtWidgets.QLabel()
        self.showEntries.setText("Show")
        # print(self.showEntries.font().family())
        self.showEntries.setFont(QtGui.QFont("MS Shell Dlg 2",10))
        self.showEntries2 = QtWidgets.QLabel()
        self.showEntries2.setText("entries")

        
        self.comboBox = QtWidgets.QComboBox()
        self.comboBox.setObjectName("comboBox")
        self.comboBox.addItem("10  ")
        self.comboBox.addItem("25  ")
        self.comboBox.addItem("50  ")
        self.comboBox.currentIndexChanged.connect(self.changeEntry)
        self.TopHlayout.addWidget(self.showEntries)
        self.TopHlayout.addWidget(self.comboBox)
        self.TopHlayout.addWidget(self.showEntries2)

        spacerItem = QtWidgets.QSpacerItem(50, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.TopHlayout.addItem(spacerItem)
        
        self.jumpLabel = QtWidgets.QLabel()
        self.jumpLabel.setText("Jump to page :")
        self.txtPage = QtWidgets.QLineEdit()
        self.txtPage.setFixedWidth(100)
        self.txtPage.setText("")
        self.txtPage.setValidator(QtGui.QIntValidator(1, 13999999))
        self.txtPage.textEdited.connect(self.PageJump)

        self.TopHlayout.addWidget(self.jumpLabel)
        self.TopHlayout.addWidget(self.txtPage)
        
        self.layout.addLayout(self.TopHlayout)
        
        self.layout.addWidget(self.conversation_table)
        
        self.Hlayout = QtWidgets.QHBoxLayout()
        
        self.next = QtWidgets.QPushButton()
        self.next.clicked.connect(self.nextButton)   
        self.next.setFixedWidth(25) 
        self.next.setFixedHeight(42) 
        self.next.setIcon(QtGui.QIcon("../icons/right.png"))
        
        self.prev = QtWidgets.QPushButton()
        self.prev.clicked.connect(self.prevButton)  
        self.prev.setIcon(QtGui.QIcon("../icons/left.png"))
        self.prev.setFixedWidth(25) 
        self.prev.setFixedHeight(42) 
        
        self.skipFirst = QtWidgets.QPushButton()
        self.skipFirst.clicked.connect(self.skipFirst_handler)   
        self.skipFirst.setFixedWidth(30) 
        self.skipFirst.setFixedHeight(42) 
        self.skipFirst.setIcon(QtGui.QIcon("../icons/skipFirst.png"))
                               
        self.skipLast = QtWidgets.QPushButton()
        self.skipLast.clicked.connect(self.skipLast_handler)  
        self.skipLast.setIcon(QtGui.QIcon("../icons/skipLast.png"))
        self.skipLast.setFixedWidth(30) 
        self.skipLast.setFixedHeight(42) 
        
        
        self.Hlayout.addWidget(self.skipFirst)
        self.Hlayout.addWidget(self.prev)
        self.Hlayout.addWidget(self.PageNumberList)
        self.Hlayout.addWidget(self.next)
        self.Hlayout.addWidget(self.skipLast)
        self.Hlayout.setContentsMargins(QMargins(0,0,0,0))
        self.Hlayout.setSpacing(0)

        self.layout.addLayout(self.Hlayout)
        
        self.setLayout(self.layout)
        self.jKey = QtWidgets.QShortcut(QKeySequence("Ctrl+j"), self,
                            self.focusTextBox, context=QtCore.Qt.WidgetWithChildrenShortcut)
        
        
    def focusTextBox(self):
        print("adf")
        self.jKey.setKey(QKeySequence("Ctrl+k"))

    def changeEntry(self):
        self.conversation_table.changePageLimit(int(self.comboBox.currentText()))

    def PageJump(self):
        if(self.txtPage.text().strip() == ""): return
        print(self.txtPage.text())
        self.conversation_table.switchPage(int(self.txtPage.text()))
        pass
    
    def eventFilter(self, source, event):
        if(event.type() == QtCore.QEvent.MouseButtonPress and
           event.buttons() == QtCore.Qt.RightButton and
           source is self.conversation_table.viewport()):
            item = self.conversation_table.itemAt(event.pos())
            #print('Global Pos:', event.globalPos())
            if item is not None:
                #print('Table Item:', item.row(), item.column())
                self.rowTemp = item.row()
                self.menu = QtWidgets.QMenu(self)
                self.action = QtWidgets.QAction("Bookmark")
                self.action.triggered.connect(self.bookMark)
                self.menu.addAction(self.action)        
                self.action2 = QtWidgets.QAction("Split Page")
                self.action2.triggered.connect(self.splitPage)
                self.menu.addAction(self.action2)        
                #menu.exec_(event.globalPos())
        return super(MyWindow, self).eventFilter(source, event)

    def bookMark(self,test):
        self.conversation_table.createBookMark(self.rowTemp)
        
    def splitPage(self):
        index = self.conversation_table.currentRow()
        self.conversation_table.splitPage(index)
       
    def generateMenu(self, pos):
        print("pos======",pos)
        self.menu.exec_(self.conversation_table.mapToGlobal(pos))   # +++

    def ListItemClicked(self):
        pageSelected = self.PageNumberList.selectedItems()[0].data(Qt.UserRole)
        self.conversation_table.switchPage(pageSelected)
        # self.conversation_table.redrawList(pageSelected)
        
    def createCustomTable(self):
        self.conversation_table.setColumnCount(3)
        item = QtWidgets.QTableWidgetItem()
        item.setText("Header1")
        self.conversation_table.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        item.setText("Header2")
        self.conversation_table.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        item.setText("Header3")
        self.conversation_table.setHorizontalHeaderItem(2, item)
        self.conversation_table.setIconSize(QtCore.QSize(32, 32))
        self.conversation_table.horizontalHeader().setStretchLastSection(True)
        # self.conversation_table.setColumnWidth(1, 400);
        self.conversation_table.setItemDelegateForColumn(1, EditorDelegate(debug=True))

    def insert_str(self, index,string, str_to_insert):
        return string[:index] + str_to_insert + string[index:]
    
    def test1(self):
        
        textItem = self.conversation_table.item(0,1)
        receivedJson = {'main': [{'entity': ['Denmark', 'GPE']}, {'entity': ['yesterday', 'DATE']}, {'entity': ['Thai', 'ORG']}, {'entity': ['yesterday', 'DATE']}, {'entity': ['Utah', 'GPE']}]}
        unqiueList = []
        for word in receivedJson["main"]:
            entity = word["entity"][0]
            en_type = word["entity"][1]
            unqiueList.append([entity,en_type])
        res = [] 
        for i,k in unqiueList: 
            matched = False
            for item in res:
                if i in item[0] and k in item[1]:
                    matched = True
                    break
            if not matched:
                res.append([i,k]) 
            
        for word in res:
            
            entity = word[0]
            en_type = word[1]
            
            text = textItem.text()
            textIndex = text.find(entity)
            text = self.insert_str(textIndex,text,"<"+en_type+">")
            
            textIndex = text.find(entity)
            text = self.insert_str(textIndex+len(entity),text,"</"+en_type+">")
            
            textItem.setText(text)
        self.conversation_table.setItem(0, 1, textItem)
    
    def test(self):
        speaker_start = QtWidgets.QTableWidgetItem()
        speaker_start.setText(str(self.c+1))
        
        t = QtWidgets.QTableWidgetItem()
        text = "Denmark yesterday. Thai yesterday. Utah, i think is chicken pie or something?"

        t.setText(text)
        self.conversation_table.insertRow(self.c)
        self.conversation_table.setItem(self.c, 0, speaker_start)
        self.conversation_table.setItem(self.c, 1, t)
        self.c = self.c + 1
        print ('success')
        
    def nextButton(self):
        self.conversation_table.nextPage()
        print ('success')
        
    def prevButton(self):
        self.conversation_table.prevPage()
        print ('success')
        #self.conversation_table.item(11,0).setText("asdf")
        
    def skipFirst_handler(self):
        self.conversation_table.switchPage(1)

    def skipLast_handler(self):
        self.conversation_table.switchPage(len(self.conversation_table.pageLimitList))

## Main method to test CustomTable class UI and Code    
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = MyWindow()
    w.show()
    sys.exit(app.exec_())