from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QBrush, QColor, QKeySequence
from functools import partial
from .growingtextedit import GrowingTextEdit
from utilities.utils import cleanhtml,insert_str
from utilities.Interpreter import Interpreter
import re

class EditorDelegate(QtWidgets.QStyledItemDelegate):
    def __init__(self, parent=None, customsignal=None, debug=False):
        self.customsignal = customsignal
        super(EditorDelegate, self).__init__(parent)
        self.doc = QtGui.QTextDocument(self)
        font = QtGui.QFont()
        font.setPointSize(15)
        self.doc.setDefaultFont(font)
        self.orginalText = ""
        self.debug = debug
        
    def createEditor(self, parent, option, index):
        textedit_widget = GrowingTextEdit(parent)
        textedit_widget.setFontPointSize(15)
        return textedit_widget


    def paint(self, painter, option, index):
        painter.save()
        options = QtWidgets.QStyleOptionViewItem(option)
        self.initStyleOption(options, index)
        
        self.doc.setHtml(Interpreter(options.text).interpret())
        options.text = ""
        style = QtWidgets.QApplication.style() if options.widget is None \
            else options.widget.style()
        style.drawControl(QtWidgets.QStyle.CE_ItemViewItem, options, painter)

        ctx = QtGui.QAbstractTextDocumentLayout.PaintContext()
        if option.state & QtWidgets.QStyle.State_Selected:
            ctx.palette.setColor(QtGui.QPalette.Text, option.palette.color(
                QtGui.QPalette.Active, QtGui.QPalette.HighlightedText))
        else:
            ctx.palette.setColor(QtGui.QPalette.Text, option.palette.color(
                QtGui.QPalette.Active, QtGui.QPalette.Text))
        textRect = style.subElementRect(QtWidgets.QStyle.SE_ItemViewItemText, options, None)
        if index.column() != 0:
            textRect.adjust(0, 0, 0, 0)
        constant = 4
        margin = (option.rect.height() - options.fontMetrics.height()) // 2
        margin = margin - constant
        textRect.setTop(textRect.top())

        painter.translate(textRect.topLeft())
        painter.setClipRect(textRect.translated(-textRect.topLeft()))
        self.doc.documentLayout().draw(painter, ctx)
        painter.restore()

    def sizeHint(self, option, index):
        return QtCore.QSize(self.doc.idealWidth(), self.doc.size().height())

    
    def setEditorData(self, editor, index):
        if self.orginalText == "":
            self.orginalText = index.data()
        editor.setPlainText(cleanhtml(index.data()))

    def getNer (self,string):
        nerList = []
        for item in Interpreter(string).findAllTag():
            pair = Interpreter(string).getEntityTagPair(item)
            nerList.append(pair)

        return nerList

    def setModelData(self, editor, model, index):
        nerList = self.getNer(self.orginalText)
        plainText = editor.toPlainText()

        for ner in nerList:   

            textIndex = plainText.find(ner[1])
            if textIndex == -1:
                continue
            plainText = insert_str(textIndex,plainText,"<"+ner[0]+">")
            
            textIndex = plainText.find(ner[1])
            plainText = insert_str(textIndex+len(ner[1]),plainText,"</"+ner[0]+">")


        model.setData(index, plainText)

    def eventFilter(self, editor, event):
        if self.debug==True:
            return  super().eventFilter(editor, event)
        if event.type() == QtCore.QEvent.FocusIn:
            if self.parent().autoplay_checkbox.isChecked():
                self.customsignal.start_signal.emit()

        if event.type() == QtCore.QEvent.FocusOut:
            self.customsignal.stop_signal.emit()

        if event.type() == QtCore.QEvent.KeyPress:
            if event.key() == QtCore.Qt.Key_Tab:
                self.customsignal.start_signal.emit()
                return True

            if event.key() == QtCore.Qt.Key_Escape:
                print("ENTER esc")
                self.customsignal.stop_signal.emit()
                self.closeEditor.emit(editor)
                
            if event.key() == QtCore.Qt.Key_Return:
                print("ENTER KEY")
                self.customsignal.stop_signal.emit()
                self.commitData.emit(editor)
                self.closeEditor.emit(editor)
                return True

            if event.modifiers() == QtCore.Qt.ControlModifier:
                if event.key() == QtCore.Qt.Key_Return:
                    self.customsignal.stop_signal.emit()
                    self.commitData.emit(editor)
                    self.closeEditor.emit(editor)
                    return True

        return super().eventFilter(editor, event)

