from PyQt5 import QtCore, QtGui, QtWidgets,Qt
import sys

class Dialog(QtWidgets.QDialog):
    """A simple file saving dialogue box. You can add text or input boxes and then retrieve the values.
    """
    def __init__(self, *args, **kwargs):
        """Inits Dialog.
 
        Attributes:
            title (str): Dialog window title
            box (QDialogButtonBox): QDialogButtonBox is a widget that allow add buttons to it and will automatically 
                use the appropriate layout for the user's desktop environment
                
                Currently there are 3 buttons added which is Save, Save as and Cancel.
                
            combo (QComboBox): QComboBox is a selection widget displays the current item, and can pop up a 
                list of selectable items. 
                
                It has the list of log/subtitle format which can be saved as (.stm, .TextGrid, .srt, .xml)
            
            radioGroup(QRadioButton): QRadioButton is a single selection widget that allows selection from a 
                group of radio buttons
                
                Purpose: Allow user to save log/subtitle with or without NER tag
                
        """
        super(Dialog, self).__init__(*args, **kwargs)
        self.setWindowFlags(QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowTitleHint)
        
        
        label = QtWidgets.QLabel("Save file as :")
        self.combo = QtWidgets.QComboBox()
        self.combo.addItems([".stm", ".TextGrid", ".srt", ".xml"])

        # Set dialog box title
        self.title = "ASR - Saving log"
        self.setWindowTitle(self.title)
        self.setModal(True)
        
        label2 = QtWidgets.QLabel("Do you want to save with color code?")
        
        self.box = QtWidgets.QDialogButtonBox()
        self.box.addButton("Save", QtWidgets.QDialogButtonBox.AcceptRole)
        self.box.addButton("Save as", QtWidgets.QDialogButtonBox.RejectRole)
        self.box.addButton("Cancel", QtWidgets.QDialogButtonBox.HelpRole)
        
        vbox = QtWidgets.QHBoxLayout()
        radiobutton1 = QtWidgets.QRadioButton("Yes")
        radiobutton1.setChecked(True)
        vbox.addWidget(radiobutton1)
        
        radiobutton2 = QtWidgets.QRadioButton("No")
        vbox.addWidget(radiobutton2)
        
        self.radioGroup = QtWidgets.QButtonGroup()
        self.radioGroup.addButton(radiobutton1,0)
        self.radioGroup.addButton(radiobutton2,1)

        lay = QtWidgets.QGridLayout(self)
        lay.addWidget(label, 0, 0)
        lay.addWidget(label2, 1, 0)
        lay.addWidget(self.combo, 0, 2)
        lay.addLayout(vbox,1,2)
        lay.addWidget(self.box, 2, 0,3,0,QtCore.Qt.AlignCenter)
        # Run the .setupUi() method to show the GUI
        self.resize(400, 120)
        
## Main method to test dialog class UI and Code
if __name__ == "__main__":
    # Create the application
    app = QtWidgets.QApplication(sys.argv)
    dlg = Dialog()
    dlg.exec()
 