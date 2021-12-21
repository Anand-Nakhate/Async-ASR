from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QBrush, QColor, QKeySequence
from functools import partial
from .growingtextedit import GrowingTextEdit
from PyQt5.QtCore import pyqtSignal as Signal

class EditorDelegate(QtWidgets.QStyledItemDelegate):
    def __init__(self, parent=None, customsignal=None):
        super(EditorDelegate, self).__init__(parent)
        self.key_dict = {}
        self.key_dict["!"] = "Shift+1"
        self.key_dict["@"] = "Shift+2"
        self.key_dict["#"] = "Shift+3"
        self.key_dict["$"] = "Shift+4"
        self.key_dict["%"] = "Shift+5"
        self.key_dict["^"] = "Shift+6"
        self.key_dict["&"] = "Shift+7"
        self.key_dict["*"] = "Shift+8"
        self.key_dict["("] = "Shift+9"
        self.key_dict[")"] = "Shift+0"
        self.key_dict["_"] = "Shift+-"
        self.key_dict["+"] = "Shift+="
        
        self.key_dict["{"] = "Shift+["
        self.key_dict["}"] = "Shift+]"
        self.key_dict["|"] = "Shift+\\"
        self.key_dict[":"] = "Shift+;"
        self.key_dict["\""] = "Shift+\'"
        self.key_dict["<"] = "Shift+,"
        self.key_dict[">"] = "Shift+."
        self.key_dict["?"] = "Shift+/"

    def createEditor(self, parent, option, index):
        textedit_widget = GrowingTextEdit(parent)
        textedit_widget.setFontPointSize(15)
        return textedit_widget

    def setEditorData(self, editor, index):
        editor.setPlainText(index.data())

    def setModelData(self, editor, model, index):
        model.setData(index, editor.toPlainText())

    def eventFilter(self, editor, event):
        # if event.type() == QtCore.QEvent.FocusIn:
        #     if self.parent().autoplay_checkbox.isChecked():
        #         self.customsignal.start_signal.emit()

        # if event.type() == QtCore.QEvent.FocusOut:
        #     self.customsignal.stop_signal.emit()
        modifiers = QtGui.QApplication.keyboardModifiers()
        
        if event.type() == QtCore.QEvent.KeyPress:
            if event.key() == QtCore.Qt.Key_Escape:
                print("Key : esc")
                self.closeEditor.emit(editor)
            
            else: 
                # if it is Ctrl Shif or Alt and a Key 
                # then change hotkey
                # modifiers and number
                # if self.validModifiers(modifiers)and event.key() >= QtCore.Qt.Key_0 and event.key() <= QtCore.Qt.Key_9 :
                #     text = self.modifierValue(modifiers)
                #     editor.setPlainText(text + "+" + chr(event.key()))
                #     self.parent().ChangeHotKey.emit(text + " + " + chr(event.key()))
                #     self.commitData.emit(editor)
                #     self.closeEditor.emit(editor)
                #     return True
                # #modifiers and letter
                # if self.validModifiers(modifiers) and event.key() >= QtCore.Qt.Key_A and event.key() <= QtCore.Qt.Key_Z:
                #     text = self.modifierValue(modifiers)
                #     editor.setPlainText(text + "+" + chr(event.key()))
                #     self.parent().ChangeHotKey.emit(text + " + " + chr(event.key()))
                #     self.commitData.emit(editor)
                #     self.closeEditor.emit(editor)
                #     return True
                # Special character
                if self.validModifiers(modifiers) and chr(event.key()) in self.key_dict:
                    editor.setPlainText(self.key_dict[chr(event.key()) ])
                    self.parent().ChangeHotKey.emit(self.key_dict[chr(event.key()) ])
                    self.commitData.emit(editor)
                    self.closeEditor.emit(editor)
                    return True
                if self.validModifiers(modifiers): 
                    text = self.modifierValue(modifiers)
                    editor.setPlainText(text + "+" + chr(event.key()))
                    self.parent().ChangeHotKey.emit(text + " + " + chr(event.key()))
                    self.commitData.emit(editor)
                    self.closeEditor.emit(editor)
                    return True
                return True
                    
                    # if event.key() == QtCore.Qt.Key_Return:
                    #     print("Key : Enter")
                    #     self.parent().ChangeHotKey.emit(modifiers,event.key())
                    #     self.commitData.emit(editor)
                    #     self.closeEditor.emit(editor)
                    #     return True



        return super().eventFilter(editor, event)

    def modifierValue(self,modifiers):
        if modifiers == QtCore.Qt.ShiftModifier:
            return "Shift"
        if modifiers == QtCore.Qt.ControlModifier:
            return "Ctrl"
        if modifiers == QtCore.Qt.AltModifier:
            return "Alt"

    def validModifiers(self,modifiers):
        if modifiers == QtCore.Qt.ShiftModifier or modifiers == QtCore.Qt.ControlModifier or modifiers == QtCore.Qt.AltModifier :
            return True










