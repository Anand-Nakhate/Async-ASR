import sys
import configparser
import requests
import json
import os
from PyQt5 import QtCore, QtGui, QtWidgets
from screens.first_screen import Ui_first_screen
from screens.introscreen import Ui_introscreen
from screens.shortcut import Ui_Help
from screens.about import Ui_About
from functools import partial
import threading
from PyQt5.QtCore import pyqtSignal as Signal
from screens.fourth_screen import Ui_fourth_screen
from utilities.utils import resource_path

class Ui_MainWindow(QtWidgets.QMainWindow):
    """Asr_GUI main window class
    
    Attributes:
            open_windows (List): Hold the list of openned windows
            config (Obj): ConfigParser object
            shortcut_action: QAction widget to open shortcut window
            
    """
    updateHotKeySignal = Signal(str,str)
    def __init__(self, parent=None):
        """Inits Ui_MainWindow.
        """
        super(Ui_MainWindow, self).__init__(parent)
        self.open_windows = []

    def setupUi(self, widget):
        """Setup the UI
        
        This method need to be called after the class has been instantiated. This method will create the GUI for
        our window.
            
        Args:
            widget (QtWidgets): Ui_introscreen
            
        """
        self.updateHotKeySignal.connect(self.updateHotKey)
        self.config = configparser.ConfigParser()
        self.config.read(resource_path('hotkey.ini'))
        
        self.setObjectName("MainWindow")
        screen_width = (self.available_width -
                        60) if self.available_width < 800 else 800
        screen_height = (self.available_height -
                         60) if self.available_height < 716 else 716
        self.resize(screen_width, screen_height)

        self.centralwidget = QtWidgets.QStackedWidget()
        self.centralwidget.setObjectName("centralwidget")
        self.setCentralWidget(self.centralwidget)
        self.centralwidget.addWidget(widget) 
        self.centralwidget.setCurrentWidget(widget)
        
        menubar = QtWidgets.QMenuBar(self)
        menubar.setGeometry(QtCore.QRect(0, 0, 800, 22))
        menubar.setObjectName("menubar")

        filemenu = menubar.addMenu("&File")

        new_action = QtWidgets.QAction('&New', self)
        new_action.setShortcut(self.config["HOTKEY"]["newsession"])
        new_action.setStatusTip('Start a new session')
        new_action.triggered.connect(partial(self.start_new, widget))
        filemenu.addAction(new_action)

        exit_action = QtWidgets.QAction('&Exit', self)
        exit_action.setShortcut(self.config["HOTKEY"]["exit"])
        exit_action.setStatusTip('Exit application')
        exit_action.triggered.connect(app.quit)
        filemenu.addAction(exit_action)

        helpbar = menubar.addMenu('Help')
        self.shortcut_action = QtWidgets.QAction('Shortcut Keys', self)
        self.shortcut_action.setShortcut(self.config["HOTKEY"]["help"])
        self.shortcut_action.setStatusTip('Display various shortcut keys')
        self.shortcut_action.triggered.connect(self.shortcut_help)
        helpbar.addAction(self.shortcut_action)

        about_action = QtWidgets.QAction('About', self)
        about_action.setStatusTip('About the application')
        about_action.triggered.connect(self.about)
        helpbar.addAction(about_action)

        self.setMenuBar(menubar)
        self.statusbar = QtWidgets.QStatusBar(self)
        self.statusbar.setObjectName("statusbar")
        self.setStatusBar(self.statusbar)

        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self):    
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("ASR", "ASR"))

    def shortcut_help(self):
        """Method to open shortcut window
        """
        self.open_windows.clear()
        shortcutscreen = Ui_Help()
        shortcutscreen.setupUi(self.updateHotKeySignal)
        shortcutscreen.show()
        self.open_windows.append(shortcutscreen)

    def about(self):
        """Method to open about us window
        """
        self.open_windows.clear()
        aboutscreen = Ui_About()
        aboutscreen.setupUi()
        aboutscreen.show()
        self.open_windows.append(aboutscreen)

    def start_new(self, widget):
        """Method to start a new session. Go back to home page
        
        Popup window will appear to prompt user for confirmation
        
        """
        current_widget = self.centralWidget().currentWidget()
        msg = QtWidgets.QMessageBox.question(self, 'New Session', "Are you sure you want to start a new sesion? Any unsaved progress will be lost.",
                                             QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No)
        if msg == QtWidgets.QMessageBox.Yes:
            if current_widget.objectName() == 'fourth_screen':
                current_widget.stop_button_handler()
            self.centralwidget.setCurrentWidget(widget)
            
    def updateHotKey(self,funct,hotkey):
        """Method to update the hotkey settings in config file
        
        Args:
            funct (int): The function associated to the hotkey
            hotkey (): New hotkey 
        
        """
        # open config file, set new hotkey and write back.
        cfgfile = open(resource_path('hotkey.ini'), "w")
        self.config.set("HOTKEY", funct, hotkey.replace(" ",""))
        self.config.write(cfgfile)
        
        # Update the hotkey
        if funct == "help":
            self.shortcut_action.setShortcut( hotkey.replace(" ",""))
        if isinstance(self.centralwidget.currentWidget(),Ui_fourth_screen):
           self.centralwidget.currentWidget().updateHotKey(funct,hotkey.replace(" ",""))

        
def prerun_check():
    """Function to check if all necessary config files is available 
        
    Return:
        bool: True if pass else False
        reason(str): Error message
        services_language_8k(List): List of Available services
        services_language_16k(List): List of Available services
        access_token(str): Access Token 

    """
    # Read all the config files
    config = configparser.ConfigParser()
    res = config.read(resource_path('services.ini'))
    hk = config.read(resource_path('hotkey.ini'))
    cc = config.read(resource_path('colorcode.ini'))
    
    # if config file doesn't exists
    if len(res) == 0:
        return False, "./services.ini doesn't exists. Please check services_example.ini to create one file.", [], []
    if len(hk) == 0:
        return False, "./hotkey.ini doesn't exists. Please check hotkey_example.ini to create one file.", [], []
    if len(cc) == 0:
        return False, "./colorcode.ini doesn't exists. Please check colorcode_example.ini to create one file.", [], []
    
    # if config file is invalid, section missing
    if 'ASR' not in config.sections():
        return False, "Section ASR missing from services.ini", [], []
    if 'SUD' not in config.sections():
        return False, "Section SUD missing from services.ini", [], []
    if 'API' not in config.sections():
        return False, "Section API missing from services.ini", [], []
    if 'HOTKEY' not in config.sections():
        return False, "Section HOTKEY missing from hotkey.ini", [], []
    if 'COLORCODE' not in config.sections():
        return False, "Section COLORCODE missing from colorcode.ini", [], []


    # Retreive the accessToken for asr services
    loginGateWay = config['ASR']['login_ip']
    email = config['ASR']['loginId']
    password = config['ASR']['pwd']
    payload = {'email':email,'password':password,'appId':'61a626bf76d00a0029259922','appSecret':'ad563139cbedcfc39ba21d480b11be5f8e7b4e1d3e715800d80b4ad7cde0c40a'}
    response = requests.post(loginGateWay,data=payload)
    receivedJson = response.json()
    access_token = receivedJson["accessToken"]
    print(access_token)
    # access_token = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6Im9ubGluZXRlc3RlckBnbWFpbC5jb20iLCJyb2xlIjoidXNlciIsIm5hbWUiOiJvbmxpbmV0ZXN0ZXIiLCJ0eXBlIjoidHJpYWwiLCJpYXQiOjE2MzgyNTkxMDAsIm5iZiI6MTYzODI1OTEwMCwiZXhwIjoxNjQwODUxMTAwLCJpc3MiOiJodHRwczovL2dhdGV3YXkuc3BlZWNobGFiLnNnIiwic3ViIjoiNjFhNWQ5ODk3NmQwMGEwMDI5MjU5ODI5In0.mpvZRifehapw8J37oAf5RPGnhge0UPVzERXmK7zhpni0SaMmoFsCCHlCxzDbIrdHrZPUfXvVo1INVo6LI7IIGyKajZkbPI7SGWA4D8MqDpNdDYUPYa2bIofyjbha6H_EzFG0tuxBzoa7JtQLx0BogQqrqtSHLn53mUiE8uQvO7Jq-m5Jap1qwreDqgRz7D4rEJLG0RvpeN9Wus5ga1jRHrHotGzXT0yQHm6T0zxQGSYa6QDSiaoo59CI0dWA7FrikocNbwEPWA95MEpR6RjzD-oOjzRuEWv6Jwox6Xnx9M1MGRPoYj71mEMPubmym8OAScSaEbkIHTOae2AFEu9G7Q"
    #access_token = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6ImFzeW5jX2FzckBudHUuZWR1LnNnIiwicm9sZSI6InVzZXIiLCJuYW1lIjoiQXN5bmMgQVNSIiwidHlwZSI6Im5vcm1hbCIsImlhdCI6MTYzODI5MzQzMywibmJmIjoxNjM4MjkzNDMzLCJleHAiOjE2NDA4ODU0MzMsImlzcyI6Imh0dHBzOi8vZ2F0ZXdheS5zcGVlY2hsYWIuc2ciLCJzdWIiOiI1ZjhlNTI2YzlmODZiODAwMjkyMzc1OWQifQ.iMD2QdeC6dXLogy5bqWzYty3ckpPE19oJeMcfA5YkfDdRxivAeKNkBZjRfLcITJ4bo4wPAYTVL9Y8yk2VfD8rHtVz7L4G0b4i9Y5VkFh-dqEkZuLZzft1cV_wStn1w6Q9I-x4CeegfWov7MJooSZUh31cSxd58F1pky1RTUpaPXx9EYxvxhtQynvoVtrvFGmbVzhWPaJt-1r1Jeb8n-b7eT1sYwUh7wNeB2W6gc3qk7PzqFXkCZBHiO33uadmqb9MzGI8BG3CbnfQEX_C8ta4701lbvglYPwxrY69aX4xTNOuWsYxTlJQ8lNGDn--Affo_vyelUhhEGHBxiineLMzw"
    # access_token = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6ImFzeW5jX2FzckBudHUuZWR1LnNnIiwicm9sZSI6InVzZXIiLCJuYW1lIjoiQXN5bmMgQVNSIiwidHlwZSI6Im5vcm1hbCIsImlhdCI6MTYzODc1NjMxNSwibmJmIjoxNjM4NzU2MzE1LCJleHAiOjE2NDEzNDgzMTUsImlzcyI6Imh0dHBzOi8vZ2F0ZXdheS5zcGVlY2hsYWIuc2ciLCJzdWIiOiI1ZjhlNTI2YzlmODZiODAwMjkyMzc1OWQifQ.2MqHUjQSiY-qY9o0zDstj_T9j87_VgBJ9MpwQlDY9bgcGOGKZmixHk59ZVuYa2ZiVSz3TxSH2udXuidyDti3c9hySstVwPIdITuCe6QXmx8SKhH5Pa0JJTUiOdjnzKd8boCTGRvhzxjfNPAzRvZtci92FR7wDUdGhL20-jUp6yOTU7tsluz9orzp5GIw74grLFhA-v9krcFCF4f4fljESM4Bq1z1o7q73pqwSBpVLHsQnr7YS1wRJP6IgbzZve2Xmv2y1TBbCsKCjMsdCor5OrWWZylrQAp70hvoZh5vz1YpP61Xmderqwibs81N3e0QJRCGBBKwBXKX8vkGbdPD-w"
    services_keys = []
    services_language_8k = []
    services_language_16k = []
    sud_keys = []

    available_languages_16k = ['ip_english_16k', 'ip_mandarin_16k',
                               'ip_eng_mandarin_16k', 'ip_eng_malay_16k',]
    available_languages_8k = ['ip_english_8k', 'ip_mandarin_8k',
                              'ip_eng_mandarin_8k', 'ip_eng_malay_8k']
    for key in config['ASR']:
        services_keys.append(key)
        if key == 'english_16k':
            services_language_16k.append('english')
        if key == 'mandarin_16k':
            services_language_16k.append('mandarin')
        if key == 'eng_mandarin_16k':
            services_language_16k.append('english-mandarin')
        if key == 'eng_malay_16k':
            services_language_16k.append('english-malay')
        if key == 'english_8k':
            services_language_8k.append('english')
        if key == 'mandarin_8k':
            services_language_8k.append('mandarin')
        if key == 'ip_eng_mandarin_8k':
            services_language_8k.append('english-mandarin')
        if key == 'ip_eng_malay_8k':
            services_language_8k.append('english-malay')


    #if 'access_token' not in services_keys:
        #return False, "Section ASR is missing access_token", [], []
    if 'silence_timeout' not in services_keys:
        return False, "Section ASR is missing silence_timeout", [], []
    if 'chunksaving_time' not in services_keys:
        return False, "Section ASR is missing chunksaving_time", [], []
    #if not any(language in services_keys for language in available_languages_16k):
        #return False, "Section ASR is missing one of ip_english_16k, ip_mandarin_16k, ip_eng_mandarin_16k, ip_eng_malay_16k", [], []
    #if not any(language in services_keys for language in available_languages_8k):
        #return False, "Section ASR is missing one of ip_english_8k, ip_mandarin_8k, ip_eng_mandarin_8k, ip_eng_malay_8k", [], []

    for key in config['SUD']:
        sud_keys.append(key)

    if 'english_url' not in sud_keys:
        return False, "Section SUD is missing url", [], [],[]
    if 'chinese_url' not in sud_keys:
        return False, "Section SUD is missing url", [], [],[]
    if 'enable_sud' not in sud_keys:
        return False, "Section SUD is missing ENABLE_SUD. Please provide a value of Y or N to ENABLE_SUD", [], [],[]
    # api_key currently not in use
    # if 'api_key' not in sud_keys:
    #     return False, "Section SUD is missing API_KEY", [], [],[]
    # if 'api_secret' not in sud_keys:
    #     return False, "Section SUD is missing API_SECRET", [], [],[]

    return True, 'Checks Passed', services_language_8k, services_language_16k,access_token

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    ui = Ui_MainWindow()
    # Check if all the necessary config files is available 
    result, reason, languages_8k, languages_16k,access_token = prerun_check()
    if not result:
        msg = QtWidgets.QMessageBox.critical(
            ui, 'Improperly configured services file', reason, QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Ok)
        sys.exit()
    ui.available_languages_8k = languages_8k
    ui.available_languages_16k = languages_16k
    ui.available_width = app.desktop().availableGeometry().width()
    ui.available_height = app.desktop().availableGeometry().height()
    ui.access_token = access_token
    
    intro_screen = Ui_introscreen()
    intro_screen.window = ui
    intro_screen.setupUi()

    ui.setupUi(intro_screen)
    
    ui.setGeometry(
        QtWidgets.QStyle.alignedRect(
            QtCore.Qt.LeftToRight,
            QtCore.Qt.AlignCenter,
            ui.size(),
            app.desktop().availableGeometry()
        )   
    )

    ui.show()

    sys.exit(app.exec_())
