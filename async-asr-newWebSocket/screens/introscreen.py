import configparser
import ast
from PyQt5 import QtCore, QtGui, QtWidgets
from .first_screen import Ui_first_screen
from utilities.utils import getDeviceInfo
from utilities.utils import getSupportedRate
from .thirdscreen import Ui_third_screen
from utilities.utils import str_to_list, resource_path
#from utilities.moduleSelectorDialog import ModuleSeletorDialog
 


class Ui_introscreen(QtWidgets.QWidget):
    """Asr_GUI introduction window
    
    In this class, the user can select the available features.
    ``Example,  New: Start a new recording
                Last: Load the last recording session
                Load: Load a new config file
                File Mode: Transcript audio file
                Transcription Mode: Transcript Editor
                
    Attributes:
        asr_logo (QLabel): Asr logo
        new_button (QPushButton): Button to start new recording
        last_button (QPushButton): Button to load last session
        load_button (QPushButton): Button to load config
        audio_button (QPushButton): Button to transcript audio file
        restore_button (QPushButton): Button to editor transcript
    
    """
    def __init__(self, window=None):
        """Inits Ui_introscreen. 
        """
        QtWidgets.QWidget.__init__(self)
        self.window = window

    def setupUi(self):
        """Setup the UI
        
        This method need to be called after the class has been instantiated. This method will create the GUI for
        our window.
    
            
        """
        self.setObjectName("introscreen")
        screen_width = (self.window.available_width -
                        50) if self.window.available_width < 700 else 700
        screen_height = (self.window.available_height -
                         50) if self.window.available_height < 700 else 700
        self.resize(screen_width, screen_height)

        self.parent_hboxLayout = QtWidgets.QHBoxLayout(self)
        self.parent_hboxLayout.setObjectName('parentlayout')
        self.parent_hboxLayout.insertStretch(0, 60)

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

        self.buttonlayout = QtWidgets.QHBoxLayout()
        self.buttonlayout.setObjectName("buttonlayout")

        self.new_button = QtWidgets.QPushButton(self)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.new_button.sizePolicy().hasHeightForWidth())
        self.new_button.setSizePolicy(sizePolicy)
        self.new_button.setObjectName("new_button")
        self.buttonlayout.addWidget(self.new_button)

        self.last_button = QtWidgets.QPushButton(self)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.last_button.sizePolicy().hasHeightForWidth())
        self.last_button.setSizePolicy(sizePolicy)
        self.last_button.setObjectName("last_button")
        self.buttonlayout.addWidget(self.last_button)

        self.load_button = QtWidgets.QPushButton(self)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.load_button.sizePolicy().hasHeightForWidth())
        self.load_button.setSizePolicy(sizePolicy)
        self.load_button.setObjectName("load_button")
        self.buttonlayout.addWidget(self.load_button)

        self.audio_button = QtWidgets.QPushButton(self)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.audio_button.sizePolicy().hasHeightForWidth())
        self.audio_button.setSizePolicy(sizePolicy)
        self.audio_button.setObjectName("audio_button")
        self.buttonlayout.addWidget(self.audio_button)

        self.restore_button = QtWidgets.QPushButton(self)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.restore_button.sizePolicy().hasHeightForWidth())
        self.restore_button.setSizePolicy(sizePolicy)
        self.restore_button.setObjectName("restore_button")
        self.buttonlayout.addWidget(self.restore_button)
       

        self.verticalLayout.addLayout(self.buttonlayout)

        self.parent_hboxLayout.addLayout(self.verticalLayout)

        self.parent_hboxLayout.addStretch(60)

        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)

        # Connect button to clicked events
        self.new_button.clicked.connect(self.new_button_handler)
        self.last_button.clicked.connect(self.last_button_handler)
        self.load_button.clicked.connect(self.load_button_handler)
        self.audio_button.clicked.connect(self.audio_button_handler)
        self.restore_button.clicked.connect(self.restore_button_handler)

    def retranslateUi(self):
        """Retranslate the UI
        """
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("introscreen", "Form"))
        self.new_button.setText(_translate("introscreen", "New"))
        self.last_button.setText(_translate("introscreen", "Last"))
        self.load_button.setText(_translate("introscreen", "Load"))
        self.audio_button.setText(_translate("introscreen", "File Mode"))
        self.restore_button.setText(_translate(
            "introscreen", "Transcription Mode"))

    def new_button_handler(self):
        """New button event handler
        
        Instantiate the Ui_first_screen, setupUI and set currentwidget to next screen
        
        """
        self.first_screen = Ui_first_screen(self.window, prev_screen=self)
        self.first_screen.setupUi()
        self.window.centralwidget.addWidget(self.first_screen)
        self.window.centralwidget.setCurrentWidget(self.first_screen)

    def load_button_handler(self):
        """Load button event handler
        
        Prompt user to select the config files
        
        """
        self.config_file = QtWidgets.QFileDialog.getOpenFileName(self, "Select configuration file",
                                                                 "./config.ini",
                                                                 "*.ini")
        if self.config_file[0] != '':
            self.config_filename = self.config_file[0].split('/')[-1]
            self.config = configparser.ConfigParser()
            self.config.read(self.config_file[0])

            if self.validate_configurationfile():
                self.window.statusbar.showMessage(
                    self.config_filename + ' selected', 2000)
                self.third_screen = Ui_third_screen(
                    self.window, preconfig_file=self.config_file[0], prev_screen=self)
                self.third_screen.setupUi()
                self.window.centralwidget.addWidget(self.third_screen)
                self.window.centralwidget.setCurrentWidget(self.third_screen)

    def last_button_handler(self):
        """Last button event handler
        
        Instantiate the Ui_third_screen, with value fron last_config file
        
        """
        self.config = configparser.ConfigParser()
        self.config.read(resource_path('last_config.ini'))
        if self.validate_configurationfile(resource_path('last_config.ini')):
            self.window.statusbar.showMessage(
                'Loading last used configuration', 2000)
            for mic in self.config['micdata']:
                print(self.config['micdata'][mic])
            self.third_screen = Ui_third_screen(
                self.window, preconfig_file='last_config.ini', prev_screen=self)
            self.third_screen.setupUi()
            self.window.centralwidget.addWidget(self.third_screen)
            self.window.centralwidget.setCurrentWidget(self.third_screen)

    def restore_button_handler(self):
        """Transciption mode event handler
        
        Instantiate the Ui_first_screen with is_restoremode = True, setupUI and set currentwidget to next screen

        """
        self.first_screen = Ui_first_screen(
            self.window, None, True, prev_screen=self)
        self.first_screen.setupUi()
        self.window.centralwidget.addWidget(self.first_screen)
        self.window.centralwidget.setCurrentWidget(self.first_screen)
        
    def audio_button_handler(self):
        """File mode event handler
        
        Instantiate the Ui_first_screen with is_filemode = True, setupUI and set currentwidget to next screen

        """
        self.first_screen = Ui_first_screen(
            self.window, is_filemode=True, prev_screen=self)
        self.first_screen.setupUi()
        self.window.centralwidget.addWidget(self.first_screen)
        self.window.centralwidget.setCurrentWidget(self.first_screen)


    def validate_configurationfile(self, filename=None):
        """Check if config file is valid
        """
        config_sections = self.config.sections()
        configfile = filename if filename is not None else self.config_file[0]
        # micdata is a required section for configuration file.
        if 'micdata' not in config_sections:
            self.window.statusbar.showMessage(
                'Section micdata missing from configuration file.', 2000)
            return False

        current_devices = getDeviceInfo()
        devids = []

        for device in current_devices:
            devids.append(device.split('Input Device id ')
                          [1].split(' -')[0])

        for device in self.config['micdata']:
            # check if device in configuration file is available or not
            if device not in devids:
                self.window.statusbar.showMessage(
                    'Device with id ' + device + ' not available. Please provide another configuration file.', 2000)

                return False

        # check if device contains ASR language or not. Add default sampling rate if language already provided. Languagte defaults to english. It is assumed that device is provided with atleast speaker name.
        for device in self.config['micdata']:
            list_data = ast.literal_eval(self.config['micdata'][device])
            supported_rate = getSupportedRate(int(device))

            try:
                for channel in list_data:
                    if not any("english" in s for s in list_data[channel]) and not any("mandarin" in s for s in list_data[channel]) and not any("english-mandarin" in s for s in list_data[channel]) and not any("english-malay" in s for s in list_data[channel]):
                        list_data[channel].insert(0, 'english')

                    if len(list_data[channel]) == 3:
                        list_data[channel][2] == supported_rate
                    else:
                        list_data[channel].append(supported_rate)

                    # if at this point list length is not 3, then this means speaker name was not provided.
                    if len(list_data[channel]) < 3:
                        list_data[channel].insert(1, 'Device: ' + device)
            except TypeError:
                self.window.statusbar.showMessage(
                    'Invalid configuration file', 2000)

                return False
            self.config['micdata'][device] = str(list_data)

            with open(configfile, 'w') as mconfigfile:
                self.config.write(mconfigfile)

        return True
    
