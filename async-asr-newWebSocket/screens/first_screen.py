import re
import os
from PyQt5 import QtCore, QtGui, QtWidgets
from .second_screen import Ui_second_screen
from .thirdscreen import Ui_third_screen
from utilities.utils import resource_path


class Ui_first_screen(QtWidgets.QWidget):
    """Asr_GUI Ui_first_screen window class
    
    Attributes:
        is_filemode (bool): Used to indicate if File mode is selected
        is_restoremode (bool): Used to indicate if transcript editor is selected
        prev_screen (QWidget): Hold the previous widget/Screen. This is used to go back to previous screen
       
    
    """
    def __init__(self, window, is_filemode=False, is_restoremode=False, prev_screen=None):
        """Inits Ui_first_screen
        
        Args:
            is_filemode (bool): True if File mode is selected else False
            is_restoremode (bool): True if transcript editor is selected else False
            prev_screen (QWidget): Previous screen


        """
        QtWidgets.QWidget.__init__(self)
        self.window = window
        self.is_filemode = is_filemode
        self.is_restoremode = is_restoremode
        self.prev_screen = prev_screen

    def setupUi(self):
        """Setup the UI
        
        This method need to be called after the class has been instantiated. This method will create the GUI for
        our window.
    
            
        """
        self.setObjectName("first_screen")
        screen_width = (self.window.available_width -
                        50) if self.window.available_width < 700 else 700
        screen_height = (self.window.available_height -
                         50) if self.window.available_height < 700 else 700
        self.setMaximumHeight(screen_height)
        self.resize(screen_width, screen_height)

        self.parent_hboxlayout = QtWidgets.QHBoxLayout(self)
        self.parent_hboxlayout.setObjectName('parentlayout')
        self.parent_hboxlayout.insertStretch(0, 141)

        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")

        self.asr_logo = QtWidgets.QLabel(self)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.asr_logo.sizePolicy().hasHeightForWidth())
        self.asr_logo.setSizePolicy(sizePolicy)
        self.asr_logo.setText("")
        self.asr_logo.setPixmap(QtGui.QPixmap(
            resource_path("./icons/ASR.png")))
        self.asr_logo.setScaledContents(True)
        self.asr_logo.setAlignment(QtCore.Qt.AlignCenter)
        self.asr_logo.setObjectName("asr_logo")
        self.verticalLayout.addWidget(self.asr_logo)

        self.components_layout = QtWidgets.QHBoxLayout()
        self.components_layout.setSizeConstraint(
            QtWidgets.QLayout.SetDefaultConstraint)
        self.components_layout.setObjectName("components_layout")

        self.input_parent_layout = QtWidgets.QVBoxLayout()
        self.input_parent_layout.setSpacing(6)
        self.input_parent_layout.setObjectName("input_parent_layout")

        self.input_layout = QtWidgets.QHBoxLayout()
        self.input_layout.setObjectName("input_layout")

        self.prevscreen_button = QtWidgets.QPushButton(self)
        self.prevscreen_button.setObjectName("prevscreen_button")
        self.input_layout.addWidget(self.prevscreen_button)

        self.num_mics = QtWidgets.QLineEdit(self)
        self.num_mics.setObjectName("num_mics")
        self.input_layout.addWidget(self.num_mics)

        self.next_button = QtWidgets.QPushButton(self)
        self.next_button.setObjectName("next_button")
        self.input_layout.addWidget(self.next_button)

        self.input_parent_layout.addLayout(self.input_layout)
        self.components_layout.addLayout(self.input_parent_layout)
        self.verticalLayout.addLayout(self.components_layout)
        self.parent_hboxlayout.addLayout(self.verticalLayout)
        self.parent_hboxlayout.addStretch(141)

        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)
        
        # Connect button to clicked events
        self.next_button.clicked.connect(self.next_click_handler)
        self.prevscreen_button.clicked.connect(self.prevscreen)

    def prevscreen(self):
        """Go back to previous screen
        """
        self.window.centralwidget.setCurrentWidget(self.prev_screen)

    def retranslateUi(self):
        """Retranslate the UI
        """
        _translate = QtCore.QCoreApplication.translate
        window_text = "ASR - Number of files" if (
            self.is_restoremode or self.is_filemode) else "ASR - Number of devices"
        self.window.setWindowTitle(_translate(window_text, window_text))
        help_text = "Enter number of files" if (
            self.is_restoremode or self.is_filemode) else "Enter number of devices"
        self.num_mics.setPlaceholderText(_translate(
            "first_screen", help_text))
        self.next_button.setText(_translate("first_screen", "Next"))
        self.prevscreen_button.setText(_translate("first_screen", "Back"))

    def keyPressEvent(self, event):
        """Key press event
        
        Connect enter key to next screen button
        
        """
        if event.key() == QtCore.Qt.Key_Enter or event.key() == QtCore.Qt.Key_Return:
            self.next_click_handler()
            
    def next_click_handler(self):
        """Next button event handler
        
        Instantiate Ui_third_screen if is_filemode or is_restoremode = True
        else Instantiate Ui_second_screen to select microphone 
        
        Raises:
            ValueError: Number of speaker is greater then 8
        """
        try:
            self.num_speakers = int(self.num_mics.text().strip())
            if self.num_speakers > 8:
                raise ValueError('Maximum 8 speakers allowed.', 'OUT_OF_LIMIT')
            if self.is_filemode:
                self.third_screen = Ui_third_screen(
                    self.window, num_mics=self.num_speakers, is_filemode=True, prev_screen=self)
                self.third_screen.setupUi()
                self.window.centralwidget.addWidget(self.third_screen)
                self.window.centralwidget.setCurrentWidget(self.third_screen)
            elif self.is_restoremode:
                self.third_screen = Ui_third_screen(
                    self.window, num_mics=self.num_speakers, is_restoremode=True, prev_screen=self)
                self.third_screen.setupUi()
                self.window.centralwidget.addWidget(self.third_screen)
                self.window.centralwidget.setCurrentWidget(self.third_screen)
            else:
                self.second_screen = Ui_second_screen(
                    self.window, self.num_speakers, prev_screen=self)
                self.second_screen.setupUi()
                self.window.centralwidget.addWidget(self.second_screen)
                self.window.centralwidget.setCurrentWidget(self.second_screen)
        except ValueError as e:
            if len(e.args) > 1:
                self.window.statusbar.showMessage(e.args[0], 2000)
            else:
                self.window.statusbar.showMessage(
                    'Please enter a numeric value', 2000)
                try:
                    self.num_speakers.clear()
                except:
                    pass
