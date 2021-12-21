import configparser
import os
import wave
import pysrt
import textgrids
import ast
import re
import pysubs2
from PyQt5 import QtCore, QtGui, QtWidgets
from datetime import datetime
from .fourth_screen import Ui_fourth_screen
from utilities.utils import str_to_list
from functools import partial
from slugify import slugify
import xml.etree.ElementTree as ET
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import (QApplication, QDialog,
                             QProgressBar, QPushButton)
import time
from sox import file_info


class Ui_third_screen(QtWidgets.QWidget):
    """Asr_GUI Ui_third_screen window class
    
    Attributes:
        config (Obj): ConfigParser object
        mic_ids (Dict) = Contain the information of microphone such as supported rate
            ``Example - {1: {1: 16000}} microphone index 1, with 16000 rate``
        preconfig_file (Obj): ConfigParser object. Read from Ui_introscreen last button
        langchoices (Dict): Store select langauge model for each selected microphone index 
            `` Example {1: {1: ['english_16000', 'Speaker 1', 16000]}} ``
        inputs (list): Contain the list of all the inputs available in this screen
        num_mics (int): Number of microphone
        is_filemode (bool): Used to indicate if File mode is selected
        is_restoremode (bool): Used to indicate if transcript editor is selected
        convo_data (List): Contain the subtitle information. E.g. Start time, end Time, Message
        prev_screen (QWidget): Hold the previous widget/Screen. This is used to go back to previous screen
        audio_path (str) = Used to to back to the previous selected file location 
        log_file (str) = Used to to back to the previous selected file location
        regex_pattern: Regular expression used to validate STM file format 
        xmlRoot: Contain the root node if user load an xml file
       
    
    """
    def __init__(self, window, mic_ids=None, num_mics=None, preconfig_file=None, is_filemode=False, is_restoremode=False, prev_screen=None):
        QtWidgets.QWidget.__init__(self)

        self.config = configparser.ConfigParser()
        self.window = window
        self.mic_ids = mic_ids
        self.preconfig_file = preconfig_file
        self.langchoices = {}
        self.inputs = []
        self.num_mics = num_mics
        self.is_filemode = is_filemode
        self.is_restoremode = is_restoremode
        self.convo_data = None
        self.prev_screen = prev_screen
        self.audio_path = None 
        self.log_file = None
        self.regex_pattern = r'(\S+)\s(\S+)\s(\S+)\s(\S+)\s(\S+)((\s(<.+>))?(\s(.+)))?'
        self.xmlRoot = {}
        if self.is_filemode or self.is_restoremode:
            self.mic_ids = {}
            for i in range(self.num_mics):
                self.mic_ids[i] = {1: 0}
        
        if self.preconfig_file is not None:
            self.mic_ids = {}
            self.config.read(self.preconfig_file)
            for mic in self.config['micdata']:
                #TO DELETE#
                print(self.config['micdata'][mic])
                list_data = ast.literal_eval(self.config['micdata'][mic])
                temp_dict = {}
                for channel in list_data:
                    temp_dict[channel] = list_data[channel][2]
                self.mic_ids[int(mic)] = temp_dict

    def setupUi(self):
        """Setup the UI
        
        This method need to be called after the class has been instantiated. This method will create the GUI for
        our window.
    
            
        """
        self.setObjectName("third_screen")
        screen_width = (self.window.available_width -
                        60) if self.window.available_width < 700 else 700
        screen_height = (self.window.available_height -
                         60) if self.window.available_height < 700 else 700
        self.setMaximumHeight(screen_height)
        self.resize(screen_width, screen_height)

        self.verticalLayout = QtWidgets.QVBoxLayout(self)
        self.verticalLayout.setSpacing(6)
        self.verticalLayout.setObjectName("verticalLayout")

        self.meeting_label = QtWidgets.QLabel(self)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.meeting_label.sizePolicy().hasHeightForWidth())
        self.meeting_label.setSizePolicy(sizePolicy)
        self.meeting_label.setAlignment(QtCore.Qt.AlignCenter)
        self.meeting_label.setObjectName("meeting_label")
        self.verticalLayout.addWidget(
            self.meeting_label, 0, QtCore.Qt.AlignHCenter | QtCore.Qt.AlignTop)

        self.meeting_edit = QtWidgets.QLineEdit(self)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.meeting_edit.sizePolicy().hasHeightForWidth())
        self.meeting_edit.setSizePolicy(sizePolicy)
        self.meeting_edit.setMinimumSize(QtCore.QSize(170, 0))
        self.meeting_edit.setObjectName("meeting_edit")
        self.verticalLayout.addWidget(
            self.meeting_edit, 0, QtCore.Qt.AlignHCenter)

        spacerItem = QtWidgets.QSpacerItem(
            20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)

        self.speaker_label = QtWidgets.QLabel(self)
        self.speaker_label.setObjectName("speaker_label")
        self.verticalLayout.addWidget(
            self.speaker_label, 0, QtCore.Qt.AlignHCenter | QtCore.Qt.AlignBottom)

        self.device_layout = QtWidgets.QGridLayout()
        self.device_layout.setContentsMargins(-1, -1, -1, 0)
        self.device_layout.setObjectName("device_layout")

        self.deviceone_layout = QtWidgets.QVBoxLayout()
        self.deviceone_layout.setContentsMargins(-1, 20, -1, 20)
        self.deviceone_layout.setObjectName("deviceone_layout")
        self.deviceone_label = QtWidgets.QLabel(self)
        self.deviceone_label.setEnabled(False)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.deviceone_label.sizePolicy().hasHeightForWidth())
        self.deviceone_label.setSizePolicy(sizePolicy)
        self.deviceone_label.setAlignment(QtCore.Qt.AlignCenter)
        self.deviceone_label.setObjectName("deviceone_label")
        self.deviceone_layout.addWidget(self.deviceone_label)
        self.deviceone_edit = QtWidgets.QLineEdit(self)
        self.deviceone_edit.setEnabled(False)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.deviceone_edit.sizePolicy().hasHeightForWidth())
        self.deviceone_edit.setSizePolicy(sizePolicy)
        self.deviceone_edit.setMinimumSize(QtCore.QSize(0, 35))
        self.setObjectName("deviceone_edit")
        self.deviceone_layout.addWidget(self.deviceone_edit)

        self.deviceone_asr_endpoint = QtWidgets.QComboBox(self)
        self.deviceone_asr_endpoint.setEnabled(False)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.deviceone_asr_endpoint.sizePolicy().hasHeightForWidth())
        self.deviceone_asr_endpoint.setSizePolicy(sizePolicy)
        self.deviceone_asr_endpoint.setMinimumSize(QtCore.QSize(0, 30))
        self.deviceone_asr_endpoint.setObjectName("deviceone_asr_endpoint")
        self.deviceone_asr_endpoint.addItem("16khz","16000")
        self.deviceone_asr_endpoint.addItem("8khz", "8000")
        self.deviceone_layout.addWidget(self.deviceone_asr_endpoint)

        self.deviceone_box = QtWidgets.QComboBox(self)
        self.deviceone_box.setEnabled(False)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.deviceone_box.sizePolicy().hasHeightForWidth())
        self.deviceone_box.setSizePolicy(sizePolicy)
        self.deviceone_box.setMinimumSize(QtCore.QSize(0, 30))
        self.deviceone_box.setObjectName("deviceone_box")
        self.deviceone_box.addItem("")
        self.deviceone_layout.addWidget(self.deviceone_box)
        self.deviceone_button = QtWidgets.QPushButton(self)
        self.deviceone_button.setEnabled(False)
        self.deviceone_button.setMinimumSize(QtCore.QSize(0, 30))
        self.deviceone_button.setObjectName("deviceone_button")
        
        
        self.deviceone_layout.addWidget(self.deviceone_button)
        self.deviceone_stm = QtWidgets.QPushButton(self)
        self.deviceone_stm.setEnabled(False)
        self.deviceone_stm.setMinimumSize(QtCore.QSize(0, 30))
        self.deviceone_stm.setObjectName("deviceone_stm")
        self.deviceone_layout.addWidget(self.deviceone_stm)
        self.inputs.append((self.deviceone_label, self.deviceone_edit,
                            self.deviceone_box, self.deviceone_button, self.deviceone_stm, self.deviceone_asr_endpoint))
        self.device_layout.addLayout(self.deviceone_layout, 0, 0, 1, 1)

        self.devicetwo_layout = QtWidgets.QVBoxLayout()
        self.devicetwo_layout.setContentsMargins(-1, 20, -1, 20)
        self.devicetwo_layout.setObjectName("devicetwo_layout")
        self.devicetwo_label = QtWidgets.QLabel(self)
        self.devicetwo_label.setEnabled(False)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.devicetwo_label.sizePolicy().hasHeightForWidth())
        self.devicetwo_label.setSizePolicy(sizePolicy)
        self.devicetwo_label.setAlignment(QtCore.Qt.AlignCenter)
        self.devicetwo_label.setObjectName("devicetwo_label")
        self.devicetwo_layout.addWidget(self.devicetwo_label)
        self.devicetwo_edit = QtWidgets.QLineEdit(self)
        self.devicetwo_edit.setEnabled(False)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.devicetwo_edit.sizePolicy().hasHeightForWidth())
        self.devicetwo_edit.setSizePolicy(sizePolicy)
        self.devicetwo_edit.setMinimumSize(QtCore.QSize(0, 35))
        self.devicetwo_edit.setObjectName("devicetwo_edit")
        self.devicetwo_layout.addWidget(self.devicetwo_edit)

        self.devicetwo_asr_endpoint = QtWidgets.QComboBox(self)
        self.devicetwo_asr_endpoint.setEnabled(False)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.devicetwo_asr_endpoint.sizePolicy().hasHeightForWidth())
        self.devicetwo_asr_endpoint.setSizePolicy(sizePolicy)
        self.devicetwo_asr_endpoint.setMinimumSize(QtCore.QSize(0, 30))
        self.devicetwo_asr_endpoint.setObjectName("devicetwo_asr_endpoint")
        self.devicetwo_asr_endpoint.addItem("16khz")
        self.devicetwo_asr_endpoint.addItem("8khz")
        self.devicetwo_layout.addWidget(self.devicetwo_asr_endpoint)

        self.devicetwo_box = QtWidgets.QComboBox(self)
        self.devicetwo_box.setEnabled(False)
        self.devicetwo_box.setMinimumSize(QtCore.QSize(0, 30))
        self.devicetwo_box.setObjectName("devicetwo_box")
        self.devicetwo_box.addItem("")
        self.devicetwo_layout.addWidget(self.devicetwo_box)
        self.devicetwo_button = QtWidgets.QPushButton(self)
        self.devicetwo_button.setEnabled(False)
        self.devicetwo_button.setMinimumSize(QtCore.QSize(0, 30))
        self.devicetwo_button.setObjectName("devicetwo_button")
        self.devicetwo_layout.addWidget(self.devicetwo_button)
        

        self.devicetwo_stm = QtWidgets.QPushButton(self)
        self.devicetwo_stm.setEnabled(False)
        self.devicetwo_stm.setMinimumSize(QtCore.QSize(0, 30))
        self.devicetwo_stm.setObjectName("devicetwo_stm")
        self.devicetwo_layout.addWidget(self.devicetwo_stm)
        self.inputs.append((self.devicetwo_label, self.devicetwo_edit,
                            self.devicetwo_box, self.devicetwo_button, self.devicetwo_stm, self.devicetwo_asr_endpoint))
        self.device_layout.addLayout(self.devicetwo_layout, 0, 1, 1, 1)

        self.devicethree_layout = QtWidgets.QVBoxLayout()
        self.devicethree_layout.setContentsMargins(-1, 20, -1, 20)
        self.devicethree_layout.setObjectName("devicethree_layout")
        self.devicethree_label = QtWidgets.QLabel(self)
        self.devicethree_label.setEnabled(False)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.devicethree_label.sizePolicy().hasHeightForWidth())
        self.devicethree_label.setSizePolicy(sizePolicy)
        self.devicethree_label.setAlignment(QtCore.Qt.AlignCenter)
        self.devicethree_label.setObjectName("devicethree_label")
        self.devicethree_layout.addWidget(self.devicethree_label)
        self.devicethree_edit = QtWidgets.QLineEdit(self)
        self.devicethree_edit.setEnabled(False)
        self.devicethree_edit.setMinimumSize(QtCore.QSize(0, 35))
        self.devicethree_edit.setObjectName("devicethree_edit")
        self.devicethree_layout.addWidget(self.devicethree_edit)

        self.devicethree_asr_endpoint = QtWidgets.QComboBox(self)
        self.devicethree_asr_endpoint.setEnabled(False)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.devicethree_asr_endpoint.sizePolicy().hasHeightForWidth())
        self.devicethree_asr_endpoint.setSizePolicy(sizePolicy)
        self.devicethree_asr_endpoint.setMinimumSize(QtCore.QSize(0, 30))
        self.devicethree_asr_endpoint.setObjectName("devicethree_asr_endpoint")
        self.devicethree_asr_endpoint.addItem("16khz")
        self.devicethree_asr_endpoint.addItem("8khz")
        self.devicethree_layout.addWidget(self.devicethree_asr_endpoint)

        self.devicethree_box = QtWidgets.QComboBox(self)
        self.devicethree_box.setEnabled(False)
        self.devicethree_box.setMinimumSize(QtCore.QSize(0, 30))
        self.devicethree_box.setObjectName("devicethree_box")
        self.devicethree_box.addItem("")
        self.devicethree_layout.addWidget(self.devicethree_box)
        self.devicethree_button = QtWidgets.QPushButton(self)
        self.devicethree_button.setEnabled(False)
        self.devicethree_button.setMinimumSize(QtCore.QSize(0, 30))
        self.devicethree_button.setObjectName("devicethree_button")
        self.devicethree_layout.addWidget(self.devicethree_button)
        self.devicethree_stm = QtWidgets.QPushButton(self)
        self.devicethree_stm.setEnabled(False)
        self.devicethree_stm.setMinimumSize(QtCore.QSize(0, 30))
        self.devicethree_stm.setObjectName("devicethree_stm")
        self.devicethree_layout.addWidget(self.devicethree_stm)
        self.inputs.append((self.devicethree_label, self.devicethree_edit,
                            self.devicethree_box, self.devicethree_button, self.devicethree_stm, self.devicethree_asr_endpoint))
        self.device_layout.addLayout(self.devicethree_layout, 0, 2, 1, 1)

        self.devicefour_layout = QtWidgets.QVBoxLayout()
        self.devicefour_layout.setContentsMargins(-1, 20, -1, 20)
        self.devicefour_layout.setObjectName("devicefour_layout")
        self.devicefour_label = QtWidgets.QLabel(self)
        self.devicefour_label.setEnabled(False)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.devicefour_label.sizePolicy().hasHeightForWidth())
        self.devicefour_label.setSizePolicy(sizePolicy)
        self.devicefour_label.setAlignment(QtCore.Qt.AlignCenter)
        self.devicefour_label.setObjectName("devicefour_label")
        self.devicefour_layout.addWidget(self.devicefour_label)
        self.devicefour_edit = QtWidgets.QLineEdit(self)
        self.devicefour_edit.setEnabled(False)
        self.devicefour_edit.setMinimumSize(QtCore.QSize(0, 35))
        self.devicefour_edit.setObjectName("devicefour_edit")
        self.devicefour_layout.addWidget(self.devicefour_edit)

        self.devicefour_asr_endpoint = QtWidgets.QComboBox(self)
        self.devicefour_asr_endpoint.setEnabled(False)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.devicefour_asr_endpoint.sizePolicy().hasHeightForWidth())
        self.devicefour_asr_endpoint.setSizePolicy(sizePolicy)
        self.devicefour_asr_endpoint.setMinimumSize(QtCore.QSize(0, 30))
        self.devicefour_asr_endpoint.setObjectName("devicefour_asr_endpoint")
        self.devicefour_asr_endpoint.addItem("16khz")
        self.devicefour_asr_endpoint.addItem("8khz")
        self.devicefour_layout.addWidget(self.devicefour_asr_endpoint)

        self.devicefour_box = QtWidgets.QComboBox(self)
        self.devicefour_box.setEnabled(False)
        self.devicefour_box.setMinimumSize(QtCore.QSize(0, 30))
        self.devicefour_box.setObjectName("devicefour_box")
        self.devicefour_box.addItem("")
        self.devicefour_layout.addWidget(self.devicefour_box)
        self.devicefour_button = QtWidgets.QPushButton(self)
        self.devicefour_button.setEnabled(False)
        self.devicefour_button.setMinimumSize(QtCore.QSize(0, 30))
        self.devicefour_button.setObjectName("devicefour_button")
        self.devicefour_layout.addWidget(self.devicefour_button)
        self.devicefour_stm = QtWidgets.QPushButton(self)
        self.devicefour_stm.setEnabled(False)
        self.devicefour_stm.setMinimumSize(QtCore.QSize(0, 30))
        self.devicefour_stm.setObjectName("devicefour_stm")
        self.devicefour_layout.addWidget(self.devicefour_stm)
        self.inputs.append((self.devicefour_label, self.devicefour_edit,
                            self.devicefour_box, self.devicefour_button, self.devicefour_stm, self.devicefour_asr_endpoint))
        self.device_layout.addLayout(self.devicefour_layout, 0, 3, 1, 1)

        self.devicefive_layout = QtWidgets.QVBoxLayout()
        self.devicefive_layout.setContentsMargins(-1, 20, -1, 20)
        self.devicefive_layout.setObjectName("devicefive_layout")
        self.devicefive_label = QtWidgets.QLabel(self)
        self.devicefive_label.setEnabled(False)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.devicefive_label.sizePolicy().hasHeightForWidth())
        self.devicefive_label.setSizePolicy(sizePolicy)
        self.devicefive_label.setAlignment(QtCore.Qt.AlignCenter)
        self.devicefive_label.setObjectName("devicefive_label")
        self.devicefive_layout.addWidget(self.devicefive_label)
        self.devicefive_edit = QtWidgets.QLineEdit(self)
        self.devicefive_edit.setEnabled(False)
        self.devicefive_edit.setMinimumSize(QtCore.QSize(0, 35))
        self.devicefive_edit.setObjectName("devicefive_edit")
        self.devicefive_layout.addWidget(self.devicefive_edit)

        self.devicefive_asr_endpoint = QtWidgets.QComboBox(self)
        self.devicefive_asr_endpoint.setEnabled(False)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.devicefive_asr_endpoint.sizePolicy().hasHeightForWidth())
        self.devicefive_asr_endpoint.setSizePolicy(sizePolicy)
        self.devicefive_asr_endpoint.setMinimumSize(QtCore.QSize(0, 30))
        self.devicefive_asr_endpoint.setObjectName("devicefive_asr_endpoint")
        self.devicefive_asr_endpoint.addItem("16khz")
        self.devicefive_asr_endpoint.addItem("8khz")
        self.devicefive_layout.addWidget(self.devicefive_asr_endpoint)

        self.devicefive_box = QtWidgets.QComboBox(self)
        self.devicefive_box.setEnabled(False)
        self.devicefive_box.setMinimumSize(QtCore.QSize(0, 30))
        self.devicefive_box.setObjectName("devicefive_box")
        self.devicefive_box.addItem("")
        self.devicefive_layout.addWidget(self.devicefive_box)
        self.devicefive_button = QtWidgets.QPushButton(self)
        self.devicefive_button.setEnabled(False)
        self.devicefive_button.setMinimumSize(QtCore.QSize(0, 30))
        self.devicefive_button.setObjectName("devicefive_button")
        self.devicefive_layout.addWidget(self.devicefive_button)
        self.devicefive_stm = QtWidgets.QPushButton(self)
        self.devicefive_stm.setEnabled(False)
        self.devicefive_stm.setMinimumSize(QtCore.QSize(0, 30))
        self.devicefive_stm.setObjectName("devicefive_stm")
        self.devicefive_layout.addWidget(self.devicefive_stm)
        self.inputs.append((self.devicefive_label, self.devicefive_edit,
                            self.devicefive_box, self.devicefive_button, self.devicefive_stm, self.devicefive_asr_endpoint))
        self.device_layout.addLayout(self.devicefive_layout, 1, 0, 1, 1)
        
        self.deviceone_button.setSizePolicy(QtWidgets.QSizePolicy.Minimum,QtWidgets.QSizePolicy.Expanding)
        self.devicefive_button.setSizePolicy(QtWidgets.QSizePolicy.Minimum,QtWidgets.QSizePolicy.Expanding)

        
        
        self.devicesix_layout = QtWidgets.QVBoxLayout()
        self.devicesix_layout.setContentsMargins(-1, 20, -1, 20)
        self.devicesix_layout.setObjectName("devicesix_layout")
        self.devicesix_label = QtWidgets.QLabel(self)
        self.devicesix_label.setEnabled(False)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.devicesix_label.sizePolicy().hasHeightForWidth())
        self.devicesix_label.setSizePolicy(sizePolicy)
        self.devicesix_label.setAlignment(QtCore.Qt.AlignCenter)
        self.devicesix_label.setObjectName("devicesix_label")
        self.devicesix_layout.addWidget(self.devicesix_label)
        self.devicesix_edit = QtWidgets.QLineEdit(self)
        self.devicesix_edit.setEnabled(False)
        self.devicesix_edit.setMinimumSize(QtCore.QSize(0, 35))
        self.devicesix_edit.setObjectName("devicesix_edit")
        self.devicesix_layout.addWidget(self.devicesix_edit)

        self.devicesix_asr_endpoint = QtWidgets.QComboBox(self)
        self.devicesix_asr_endpoint.setEnabled(False)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.devicesix_asr_endpoint.sizePolicy().hasHeightForWidth())
        self.devicesix_asr_endpoint.setSizePolicy(sizePolicy)
        self.devicesix_asr_endpoint.setMinimumSize(QtCore.QSize(0, 30))
        self.devicesix_asr_endpoint.setObjectName("devicesix_asr_endpoint")
        self.devicesix_asr_endpoint.addItem("16khz")
        self.devicesix_asr_endpoint.addItem("8khz")
        self.devicesix_layout.addWidget(self.devicesix_asr_endpoint)

        self.devicesix_box = QtWidgets.QComboBox(self)
        self.devicesix_box.setEnabled(False)
        self.devicesix_box.setMinimumSize(QtCore.QSize(0, 30))
        self.devicesix_box.setObjectName("devicesix_box")
        self.devicesix_box.addItem("")
        self.devicesix_layout.addWidget(self.devicesix_box)
        self.devicesix_button = QtWidgets.QPushButton(self)
        self.devicesix_button.setEnabled(False)
        self.devicesix_button.setMinimumSize(QtCore.QSize(0, 30))
        self.devicesix_button.setObjectName("devicesix_button")

        self.devicesix_layout.addWidget(self.devicesix_button)
        self.devicesix_stm = QtWidgets.QPushButton(self)
        self.devicesix_stm.setEnabled(False)
        self.devicesix_stm.setMinimumSize(QtCore.QSize(0, 30))
        self.devicesix_stm.setObjectName("devicesix_stm")
        self.devicesix_layout.addWidget(self.devicesix_stm)
        self.inputs.append((self.devicesix_label, self.devicesix_edit,
                            self.devicesix_box, self.devicesix_button, self.devicesix_stm, self.devicesix_asr_endpoint))
        self.device_layout.addLayout(self.devicesix_layout, 1, 1, 1, 1)

        self.deviceseven_layout = QtWidgets.QVBoxLayout()
        self.deviceseven_layout.setContentsMargins(-1, 20, -1, 20)
        self.deviceseven_layout.setObjectName("deviceseven_layout")
        self.deviceseven_label = QtWidgets.QLabel(self)
        self.deviceseven_label.setEnabled(False)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.deviceseven_label.sizePolicy().hasHeightForWidth())
        self.deviceseven_label.setSizePolicy(sizePolicy)
        self.deviceseven_label.setAlignment(QtCore.Qt.AlignCenter)
        self.deviceseven_label.setObjectName("deviceseven_label")
        self.deviceseven_layout.addWidget(self.deviceseven_label)
        self.deviceseven_edit = QtWidgets.QLineEdit(self)
        self.deviceseven_edit.setEnabled(False)
        self.deviceseven_edit.setMinimumSize(QtCore.QSize(0, 35))
        self.deviceseven_edit.setObjectName("deviceseven_edit")
        self.deviceseven_layout.addWidget(self.deviceseven_edit)

        self.deviceseven_asr_endpoint = QtWidgets.QComboBox(self)
        self.deviceseven_asr_endpoint.setEnabled(False)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.deviceseven_asr_endpoint.sizePolicy().hasHeightForWidth())
        self.deviceseven_asr_endpoint.setSizePolicy(sizePolicy)
        self.deviceseven_asr_endpoint.setMinimumSize(QtCore.QSize(0, 30))
        self.deviceseven_asr_endpoint.setObjectName("deviceseven_asr_endpoint")
        self.deviceseven_asr_endpoint.addItem("16khz")
        self.deviceseven_asr_endpoint.addItem("8khz")
        self.deviceseven_layout.addWidget(self.deviceseven_asr_endpoint)

        self.deviceseven_box = QtWidgets.QComboBox(self)
        self.deviceseven_box.setEnabled(False)
        self.deviceseven_box.setMinimumSize(QtCore.QSize(0, 30))
        self.deviceseven_box.setObjectName("deviceseven_box")
        self.deviceseven_box.addItem("")
        self.deviceseven_layout.addWidget(self.deviceseven_box)
        self.deviceseven_button = QtWidgets.QPushButton(self)
        self.deviceseven_button.setEnabled(False)
        self.deviceseven_button.setMinimumSize(QtCore.QSize(0, 30))
        self.deviceseven_button.setObjectName("deviceseven_button")
        self.deviceseven_layout.addWidget(self.deviceseven_button)
        self.deviceseven_stm = QtWidgets.QPushButton(self)
        self.deviceseven_stm.setEnabled(False)
        self.deviceseven_stm.setMinimumSize(QtCore.QSize(0, 30))
        self.deviceseven_stm.setObjectName("deviceseven_stm")
        self.deviceseven_layout.addWidget(self.deviceseven_stm)
        self.inputs.append((self.deviceseven_label, self.deviceseven_edit,
                            self.deviceseven_box, self.deviceseven_button, self.deviceseven_stm, self.deviceseven_asr_endpoint))
        self.device_layout.addLayout(self.deviceseven_layout, 1, 2, 1, 1)

        self.deviceeight_layout = QtWidgets.QVBoxLayout()
        self.deviceeight_layout.setContentsMargins(-1, 20, -1, 20)
        self.deviceeight_layout.setObjectName("deviceeight_layout")
        self.deviceeight_label = QtWidgets.QLabel(self)
        self.deviceeight_label.setEnabled(False)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.deviceeight_label.sizePolicy().hasHeightForWidth())
        self.deviceeight_label.setSizePolicy(sizePolicy)
        self.deviceeight_label.setAlignment(QtCore.Qt.AlignCenter)
        self.deviceeight_label.setObjectName("deviceeight_label")
        self.deviceeight_layout.addWidget(self.deviceeight_label)
        self.deviceeight_edit = QtWidgets.QLineEdit(self)
        self.deviceeight_edit.setEnabled(False)
        self.deviceeight_edit.setMinimumSize(QtCore.QSize(0, 35))
        self.deviceeight_edit.setObjectName("deviceeight_edit")
        self.deviceeight_layout.addWidget(self.deviceeight_edit)

        self.deviceeight_asr_endpoint = QtWidgets.QComboBox(self)
        self.deviceeight_asr_endpoint.setEnabled(False)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.deviceeight_asr_endpoint.sizePolicy().hasHeightForWidth())
        self.deviceeight_asr_endpoint.setSizePolicy(sizePolicy)
        self.deviceeight_asr_endpoint.setMinimumSize(QtCore.QSize(0, 30))
        self.deviceeight_asr_endpoint.setObjectName("deviceeight_asr_endpoint")
        self.deviceeight_asr_endpoint.addItem("16khz")
        self.deviceeight_asr_endpoint.addItem("8khz")
        self.deviceeight_layout.addWidget(self.deviceeight_asr_endpoint)

        self.deviceeight_box = QtWidgets.QComboBox(self)
        self.deviceeight_box.setEnabled(False)
        self.deviceeight_box.setMinimumSize(QtCore.QSize(0, 30))
        self.deviceeight_box.setObjectName("deviceeight_box")
        self.deviceeight_box.addItem("")
        self.deviceeight_layout.addWidget(self.deviceeight_box)
        self.deviceeight_button = QtWidgets.QPushButton(self)
        self.deviceeight_button.setEnabled(False)
        self.deviceeight_button.setMinimumSize(QtCore.QSize(0, 30))
        self.deviceeight_button.setObjectName("deviceeight_button")
        self.deviceeight_layout.addWidget(self.deviceeight_button)
        self.deviceeight_stm = QtWidgets.QPushButton(self)
        self.deviceeight_stm.setEnabled(False)
        self.deviceeight_stm.setMinimumSize(QtCore.QSize(0, 30))
        self.deviceeight_stm.setObjectName("deviceeight_stm")
        self.deviceeight_layout.addWidget(self.deviceeight_stm)
        self.inputs.append((self.deviceeight_label, self.deviceeight_edit,
                            self.deviceeight_box, self.deviceeight_button, self.deviceeight_stm, self.deviceeight_asr_endpoint))
        self.device_layout.addLayout(self.deviceeight_layout, 1, 3, 1, 1)

        self.device_layout.setRowStretch(0, 1)
        self.device_layout.setRowStretch(1, 1)
        self.verticalLayout.addLayout(self.device_layout)

        spacerItem1 = QtWidgets.QSpacerItem(
            20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem1)

        self.config_layout = QtWidgets.QGridLayout()
        self.config_layout.setObjectName("config_layout")

        self.config_checkbox = QtWidgets.QCheckBox(self)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.config_checkbox.sizePolicy().hasHeightForWidth())
        self.config_checkbox.setSizePolicy(sizePolicy)
        self.config_checkbox.setObjectName("config_checkbox")
        self.config_layout.addWidget(
            self.config_checkbox, 1, 0, 1, 1, QtCore.Qt.AlignCenter)

        self.config_edit = QtWidgets.QLineEdit(self)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.config_edit.sizePolicy().hasHeightForWidth())
        self.config_edit.setSizePolicy(sizePolicy)
        self.config_edit.setMinimumSize(QtCore.QSize(210, 0))
        self.config_edit.setObjectName("config_edit")
        self.config_edit.hide()
        self.config_layout.addWidget(
            self.config_edit, 1, 1, 1, 1, QtCore.Qt.AlignLeft)

        self.verticalLayout.addLayout(self.config_layout)

        self.prevscreen_button = QtWidgets.QPushButton(self)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.prevscreen_button.sizePolicy().hasHeightForWidth())
        self.prevscreen_button.setSizePolicy(sizePolicy)
        self.prevscreen_button.setObjectName("prevscreen_button")
        self.verticalLayout.addWidget(
            self.prevscreen_button, 0, QtCore.Qt.AlignHCenter)

        self.next_button = QtWidgets.QPushButton(self)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.next_button.sizePolicy().hasHeightForWidth())
        self.next_button.setSizePolicy(sizePolicy)
        self.next_button.setObjectName("next_button")
        self.verticalLayout.addWidget(
            self.next_button, 0, QtCore.Qt.AlignHCenter)

        self.audio_split_button = QtWidgets.QPushButton(self)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.audio_split_button.sizePolicy().hasHeightForWidth())
        self.audio_split_button.setSizePolicy(sizePolicy)
        self.audio_split_button.setObjectName("audio_split_button")
        self.verticalLayout.addWidget(
            self.audio_split_button, 0, QtCore.Qt.AlignHCenter)

        

        self.progress = QProgressBar(self)
        self.progress.setAlignment(QtCore.Qt.AlignCenter) 
        self.progress.hide()
        self.verticalLayout.addWidget(self.progress, 0, QtCore.Qt.AlignHCenter)
        self.retranslateUi()

        QtCore.QMetaObject.connectSlotsByName(self)

        self.next_button.clicked.connect(self.next_button_handler)
        self.prevscreen_button.clicked.connect(self.prevscreen_handler)
        self.audio_split_button.clicked.connect(
            partial(self.audio_file_split_handler, self.audio_split_button))
        self.config_checkbox.stateChanged.connect(self.state_changed)
        self.deviceone_button.clicked.connect(
            partial(self.audio_file_selector, self.deviceone_button))
        self.devicetwo_button.clicked.connect(
            partial(self.audio_file_selector, self.devicetwo_button))
        self.devicethree_button.clicked.connect(
            partial(self.audio_file_selector, self.devicethree_button))
        self.devicefour_button.clicked.connect(
            partial(self.audio_file_selector, self.devicefour_button))
        self.devicefive_button.clicked.connect(
            partial(self.audio_file_selector, self.devicefive_button))
        self.devicesix_button.clicked.connect(
            partial(self.audio_file_selector, self.devicesix_button))
        self.deviceseven_button.clicked.connect(
            partial(self.audio_file_selector, self.deviceseven_button))
        self.deviceeight_button.clicked.connect(
            partial(self.audio_file_selector, self.deviceeight_button))
        self.deviceone_stm.clicked.connect(
            partial(self.log_file_selector, self.deviceone_stm))
        self.devicetwo_stm.clicked.connect(
            partial(self.log_file_selector, self.devicetwo_stm))
        self.devicethree_stm.clicked.connect(
            partial(self.log_file_selector, self.devicethree_stm))
        self.devicefour_stm.clicked.connect(
            partial(self.log_file_selector, self.devicefour_stm))
        self.devicefive_stm.clicked.connect(
            partial(self.log_file_selector, self.devicefive_stm))
        self.devicesix_stm.clicked.connect(
            partial(self.log_file_selector, self.devicesix_stm))
        self.deviceseven_stm.clicked.connect(
            partial(self.log_file_selector, self.deviceseven_stm))
        self.deviceeight_stm.clicked.connect(
            partial(self.log_file_selector, self.deviceeight_stm))
        self.deviceone_asr_endpoint.currentTextChanged.connect(
            partial(self.asr_endpoint_selector, self.deviceone_box))
        self.devicetwo_asr_endpoint.currentTextChanged.connect(
            partial(self.asr_endpoint_selector, self.devicetwo_box))
        self.devicethree_asr_endpoint.currentTextChanged.connect(
            partial(self.asr_endpoint_selector, self.devicethree_box))
        self.devicefour_asr_endpoint.currentTextChanged.connect(
            partial(self.asr_endpoint_selector, self.devicefour_box))
        self.devicefive_asr_endpoint.currentTextChanged.connect(
            partial(self.asr_endpoint_selector, self.devicefive_box))
        self.devicesix_asr_endpoint.currentTextChanged.connect(
            partial(self.asr_endpoint_selector, self.devicesix_box))
        self.deviceseven_asr_endpoint.currentTextChanged.connect(
            partial(self.asr_endpoint_selector, self.deviceseven_box))
        self.deviceeight_asr_endpoint.currentTextChanged.connect(
            partial(self.asr_endpoint_selector, self.deviceeight_box))

    def retranslateUi(self):
        """Retranslate the UI
        """
        _translate = QtCore.QCoreApplication.translate
        self.window.setWindowTitle(_translate(
            "ASR - Session Details", "ASR - Session Details"))
        self.meeting_label.setText(_translate(
            "third_screen", "Meeting Details"))
        self.meeting_edit.setPlaceholderText(
            _translate("third_screen", "Enter meeting name"))
        self.speaker_label.setText(_translate(
            "third_screen", "Speaker Details"))

        self.deviceone_edit.setPlaceholderText(
            _translate("third_screen", "Enter name for device 1"))
        self.deviceone_box.setCurrentText(
            _translate("third_screen", self.window.available_languages_16k[0]))
        self.deviceone_box.setItemText(
            0, _translate("third_screen", self.window.available_languages_16k[0]))
        self.deviceone_button.setText(_translate(
            "third_screen", "Select Audio File"))
        self.deviceone_stm.setText(_translate(
            "third_screen", "Select log File"))

        self.devicetwo_help = 'File: 2' if (
            self.is_filemode or self.is_restoremode) else 'Device 2'
        self.devicetwo_label.setText(_translate(
            "third_screen", self.devicetwo_help))
        self.devicetwo_edit.setPlaceholderText(
            _translate("third_screen", "Enter name for device 2"))
        self.devicetwo_box.setItemText(
            0, _translate("third_screen", self.window.available_languages_16k[0]))
        self.devicetwo_button.setText(_translate(
            "third_screen", "Select Audio File"))
        self.devicetwo_stm.setText(_translate(
            "third_screen", "Select log File"))

        self.devicethree_help = 'File: 3' if (
            self.is_filemode or self.is_restoremode) else 'Device 3'
        self.devicethree_label.setText(_translate(
            "third_screen", self.devicethree_help))
        self.devicethree_edit.setPlaceholderText(
            _translate("third_screen", "Enter name for device 3"))
        self.devicethree_box.setItemText(
            0, _translate("third_screen", self.window.available_languages_16k[0]))
        self.devicethree_button.setText(
            _translate("third_screen", "Select Audio File"))
        self.devicethree_stm.setText(
            _translate("third_screen", "Select log File"))

        self.devicefour_help = 'File: 4' if (
            self.is_filemode or self.is_restoremode) else 'Device 4'
        self.devicefour_label.setText(_translate(
            "third_screen", self.devicefour_help))
        self.devicefour_edit.setPlaceholderText(
            _translate("third_screen", "Enter name for device 4"))
        self.devicefour_box.setItemText(
            0, _translate("third_screen", self.window.available_languages_16k[0]))
        self.devicefour_button.setText(
            _translate("third_screen", "Select Audio File"))
        self.devicefour_stm.setText(_translate(
            "third_screen", "Select log File"))

        self.devicefive_help = 'File: 5' if (
            self.is_filemode or self.is_restoremode) else 'Device 5'
        self.devicefive_label.setText(_translate(
            "third_screen", self.devicefive_help))
        self.devicefive_edit.setPlaceholderText(
            _translate("third_screen", "Enter name for device 5"))
        self.devicefive_box.setItemText(
            0, _translate("third_screen", self.window.available_languages_16k[0]))
        self.devicefive_button.setText(
            _translate("third_screen", "Select Audio File"))
        self.devicefive_stm.setText(_translate(
            "third_screen", "Select log File"))

        self.devicesix_help = 'File: 6' if (
            self.is_filemode or self.is_restoremode) else 'Device 6'
        self.devicesix_label.setText(_translate(
            "third_screen", self.devicesix_help))
        self.devicesix_edit.setPlaceholderText(
            _translate("third_screen", "Enter name for device 6"))
        self.devicesix_box.setItemText(
            0, _translate("third_screen", self.window.available_languages_16k[0]))
        self.devicesix_button.setText(_translate(
            "third_screen", "Select Audio File"))
        self.devicesix_stm.setText(_translate(
            "third_screen", "Select log File"))

        self.deviceseven_help = 'File: 7' if (
            self.is_filemode or self.is_restoremode) else 'Device 7'
        self.deviceseven_label.setText(_translate(
            "third_screen", self.deviceseven_help))
        self.deviceseven_edit.setPlaceholderText(
            _translate("third_screen", "Enter name for device 7"))
        self.deviceseven_box.setItemText(
            0, _translate("third_screen", self.window.available_languages_16k[0]))
        self.deviceseven_button.setText(
            _translate("third_screen", "Select Audio File"))
        self.deviceseven_stm.setText(
            _translate("third_screen", "Select log File"))

        self.deviceeight_help = 'File: 8' if (
            self.is_filemode or self.is_restoremode) else 'Device 8'
        self.deviceeight_label.setText(_translate(
            "third_screen", self.deviceeight_help))
        self.deviceeight_edit.setPlaceholderText(
            _translate("third_screen", "Enter name for device 8"))
        self.deviceeight_box.setItemText(
            0, _translate("third_screen", self.window.available_languages_16k[0]))
        self.deviceeight_button.setText(
            _translate("third_screen", "Select Audio File"))
        self.deviceeight_stm.setText(
            _translate("third_screen", "Select log File"))
        self.prevscreen_button.setText(_translate("third_screen", "Back"))
        self.audio_split_button.setText(_translate("third_screen", "Split Audio"))
        self.audio_split_button.show() if (
            self.is_filemode or self.is_restoremode) else self.audio_split_button.hide()

        self.config_checkbox.hide() if (
            self.is_filemode or self.is_restoremode) else self.config_checkbox.show()

        self.deviceone_button.show() if (
            self.is_filemode or self.is_restoremode) else self.deviceone_button.hide()
        self.devicetwo_button.show() if (
            self.is_filemode or self.is_restoremode) else self.devicetwo_button.hide()
        self.devicethree_button.show() if (
            self.is_filemode or self.is_restoremode) else self.devicethree_button.hide()
        self.devicefour_button.show() if (
            self.is_filemode or self.is_restoremode) else self.devicefour_button.hide()
        self.devicefive_button.show() if (
            self.is_filemode or self.is_restoremode) else self.devicefive_button.hide()
        self.devicesix_button.show() if (
            self.is_filemode or self.is_restoremode) else self.devicesix_button.hide()
        self.deviceseven_button.show() if (
            self.is_filemode or self.is_restoremode) else self.deviceseven_button.hide()
        self.deviceeight_button.show() if (
            self.is_filemode or self.is_restoremode) else self.deviceeight_button.hide()

        self.deviceone_stm.show() if self.is_restoremode else self.deviceone_stm.hide()
        self.devicetwo_stm.show() if self.is_restoremode else self.devicetwo_stm.hide()
        self.devicethree_stm.show() if self.is_restoremode else self.devicethree_stm.hide()
        self.devicefour_stm.show() if self.is_restoremode else self.devicefour_stm.hide()
        self.devicefive_stm.show() if self.is_restoremode else self.devicefive_stm.hide()
        self.devicesix_stm.show() if self.is_restoremode else self.devicesix_stm.hide()
        self.deviceseven_stm.show() if self.is_restoremode else self.deviceseven_stm.hide()
        self.deviceeight_stm.show() if self.is_restoremode else self.deviceeight_stm.hide()

        self.deviceone_edit.show() if not self.is_restoremode else self.deviceone_edit.hide()
        self.devicetwo_edit.show() if not self.is_restoremode else self.devicetwo_edit.hide()
        self.devicethree_edit.show() if not self.is_restoremode else self.devicethree_edit.hide()
        self.devicefour_edit.show() if not self.is_restoremode else self.devicefour_edit.hide()
        self.devicefive_edit.show() if not self.is_restoremode else self.devicefive_edit.hide()
        self.devicesix_edit.show() if not self.is_restoremode else self.devicesix_edit.hide()
        self.deviceseven_edit.show() if not self.is_restoremode else self.deviceseven_edit.hide()
        self.deviceeight_edit.show() if not self.is_restoremode else self.deviceeight_edit.hide()

        self.deviceone_box.show() if not self.is_restoremode else self.deviceone_box.hide()
        self.devicetwo_box.show() if not self.is_restoremode else self.devicetwo_box.hide()
        self.devicethree_box.show() if not self.is_restoremode else self.devicethree_box.hide()
        self.devicefour_box.show() if not self.is_restoremode else self.devicefour_box.hide()
        self.devicefive_box.show() if not self.is_restoremode else self.devicefive_box.hide()
        self.devicesix_box.show() if not self.is_restoremode else self.devicesix_box.hide()
        self.deviceseven_box.show() if not self.is_restoremode else self.deviceseven_box.hide()
        self.deviceeight_box.show() if not self.is_restoremode else self.deviceeight_box.hide()

        self.deviceone_asr_endpoint.show(
        ) if not self.is_restoremode else self.deviceone_asr_endpoint.hide()
        self.devicetwo_asr_endpoint.show(
        ) if not self.is_restoremode else self.devicetwo_asr_endpoint.hide()
        self.devicethree_asr_endpoint.show(
        ) if not self.is_restoremode else self.devicethree_asr_endpoint.hide()
        self.devicefour_asr_endpoint.show(
        ) if not self.is_restoremode else self.devicefour_asr_endpoint.hide()
        self.devicefive_asr_endpoint.show(
        ) if not self.is_restoremode else self.devicefive_asr_endpoint.hide()
        self.devicesix_asr_endpoint.show(
        ) if not self.is_restoremode else self.devicesix_asr_endpoint.hide()
        self.deviceseven_asr_endpoint.show(
        ) if not self.is_restoremode else self.deviceseven_asr_endpoint.hide()
        self.deviceeight_asr_endpoint.show(
        ) if not self.is_restoremode else self.deviceeight_asr_endpoint.hide()

        self.config_checkbox.setText(_translate("third_screen", "Save Config"))
        self.config_edit.setPlaceholderText(_translate(
            "third_screen", "Enter configuration file name"))
        self.next_button.setText(_translate("third_screen", "Next"))

        self.activate_inputs()

        self.window.setGeometry(
            QtWidgets.QStyle.alignedRect(
                QtCore.Qt.LeftToRight,
                QtCore.Qt.AlignCenter,
                self.window.size(),
                QtWidgets.QApplication.desktop().availableGeometry()
            )
        )

        if self.preconfig_file is not None:
            currindex = 0
            if 'meeting_name' in self.config.sections():
                self.meeting_edit.setText(self.config['meeting_name']['name'])
            for data in self.config['micdata']:
                list_data = ast.literal_eval(self.config['micdata'][data])
                for channel in list_data:
                    self.inputs[currindex][0].setText('Device ID: ' + str(data) + ' Channel: ' + str(channel))
                    self.inputs[currindex][1].setText(list_data[channel][1])
                    item_index = self.inputs[currindex][2].findText(list_data[channel][0].split('_')[0])
                    self.inputs[currindex][2].setCurrentIndex(item_index)
                    currindex = currindex + 1

    def prevscreen_handler(self):
        """Go back to previous screen
        """
        self.window.centralwidget.setCurrentWidget(self.prev_screen)

    def state_changed(self, integer):
        if self.config_checkbox.isChecked():
            self.config_layout.setAlignment(
                self.config_checkbox, QtCore.Qt.AlignRight)
            self.config_edit.show()
        else:
            self.config_layout.setAlignment(
                self.config_checkbox, QtCore.Qt.AlignCenter)
            self.config_edit.hide()

    def validate_addframerate_audio_inputs(self):
        """Validate and add framerate of audio file
        
        Return:
            True if input file is valid else False
        
        """
        for index, key in enumerate(self.mic_ids):
            audio_format = '.wav'
            if not self.inputs[index][3].text().strip().endswith(audio_format, -4):
                self.window.statusbar.showMessage(
                    'Please select a wav file for speaker ' + str(index + 1), 2000)
                return False
            self.window.statusbar.showMessage('Checks passed', 2000)

        for index, key in enumerate(self.mic_ids):
            wf = wave.open(self.inputs[index][3].property('filepath')[0][0])
            self.mic_ids[key][1] = wf.getframerate()
            wf.close()
        return True

    def next_button_handler(self):
        """Next button event handler
        
        Instantiate Ui_fourth_screen
        
        """
        # self.calc = External()
        # self.calc.countChanged.connect(self.onCountChanged)
        # self.calc.start()
        meeting_name = self.meeting_edit.text().strip()

        if meeting_name == '':
            meeting_name = 'meeting_' + datetime.now().strftime('%d-%m-%Y_%H_%M_%S')

        if os.path.exists('recordings/' + meeting_name + '/'):
            self.window.statusbar.showMessage(
                'Meeting already exists, please try another name.', 2000)
            return

        # validate audio file
        if self.is_filemode:
            if not self.validate_addframerate_audio_inputs():
                return

        if self.is_restoremode:
            if not self.validate_addframerate_audio_inputs():
                return

            for index, key in enumerate(self.mic_ids):
                log_format = ['stm', 'srt', 'TextGrid', 'txt', 'sub', 'vtt','xml']
                current_format = self.inputs[index][4].text().strip().split('.')[-1]

                if current_format not in log_format:
                    self.window.statusbar.showMessage(
                        'Please select a log file for speaker ' + str(index + 1), 2000)

                    return

                self.window.statusbar.showMessage('Checks passed', 2000)

            self.langchoices, self.convo_data,self.xmlRoot = self.restoremode_data()

        if self.config_checkbox.isChecked() and self.config_edit.text().strip() == '':
            self.window.statusbar.showMessage(
                'Please enter a configuration file name.', 2000)

            return

        if not self.is_restoremode:
            currindex = 0
            for index, mic in enumerate(self.mic_ids):
                temp_dict = {}
                for channel in self.mic_ids[mic]:
                    # mic_choice = self.inputs[currindex][2].itemText(self.inputs[currindex][2].currentIndex())
                    mic_choice = self.inputs[currindex][2].itemData(
                        self.inputs[currindex][2].currentIndex(), QtCore.Qt.UserRole)
                    mic_name = self.inputs[currindex][1].text().strip()
                    temp_dict[channel] = []
                    temp_dict[channel].append(mic_choice)
                    temp_dict[channel].append(mic_name)
                    temp_dict[channel].append(self.mic_ids[mic][channel])
                    if self.is_filemode:
                        temp_dict[channel].append(
                            self.inputs[currindex][3].property('filepath')[0])
                    currindex = currindex + 1

                self.langchoices[mic] = temp_dict

        if not (self.is_filemode or self.is_restoremode):
            self.config['micdata'] = self.langchoices
            self.config['meeting_name'] = {'name': meeting_name}
            with open('last_config.ini', 'w') as mconfigfile:
                self.config.write(mconfigfile)

        if not os.path.exists('configs/'):
            os.makedirs('configs/')

        if self.config_checkbox.isChecked():
            with open('configs/' + self.config_edit.text().strip() + '.ini', 'w') as mconfigfile:
                self.config.write(mconfigfile)
        
        self.fourth_screen = Ui_fourth_screen(self.window, self.langchoices, slugify(
            meeting_name), self.num_mics, self.is_filemode, self.is_restoremode, self.convo_data, self.xmlRoot, self.progress,prev_screen=self)
        self.fourth_screen.setupUi()
        self.window.centralwidget.addWidget(self.fourth_screen)
        self.window.centralwidget.setCurrentWidget(self.fourth_screen)
        self.window.showMaximized()


    def activate_inputs(self):
        """Enable the input base on the number of speaker

        """
        currindex = 0
        for key in self.mic_ids:
            resample_rate = 8000 if self.mic_ids[key][1] == 8000 else 16000
            for channel in self.mic_ids[key]:
                self.inputs[currindex][0].setEnabled(True)
                help_text = "File: " + str(currindex + 1) if (
                    self.is_filemode or self.is_restoremode) else 'Device ID: ' + str(key) + ' Channel: ' + str(channel)
                self.inputs[currindex][0].setText(help_text)
                self.inputs[currindex][1].setEnabled(True)
                self.inputs[currindex][1].setText(
                    'Speaker ' + str(currindex+1))
                self.inputs[currindex][2].setEnabled(True)
                self.inputs[currindex][5].setEnabled(True)
                self.inputs[currindex][2].setItemText(
                    0, self.window.available_languages_16k[0])
                self.inputs[currindex][2].setItemData(
                    0, self.window.available_languages_16k[0] + '_' + str(resample_rate), QtCore.Qt.UserRole)
                for index, data in enumerate(self.window.available_languages_16k):
                    if index != 0:
                        self.inputs[currindex][2].addItem(data)
                        self.inputs[currindex][2].setItemData(
                            index, data + '_' + str(resample_rate), QtCore.Qt.UserRole)

                if self.is_filemode or self.is_restoremode:
                    self.inputs[currindex][3].setEnabled(True)

                if self.is_restoremode:
                    self.inputs[currindex][4].setEnabled(True)

                currindex = currindex + 1

    def audio_file_selector(self, selector_button):
        """Audio file openner 
        
        Args:
            selector_button (QPushButton): Reference to QPushButton, used to change the text after an audio file is selected
        """
        
        # self.audio_path is None open file directory at the current location
        # Else open at the previous directory
        if self.audio_path != None:
            self.wav_file = QtWidgets.QFileDialog.getOpenFileNames(self, "Select wav file", self.audio_path[0], "*.wav")
        else:
            self.wav_file = QtWidgets.QFileDialog.getOpenFileNames(self, "Select wav file", ".", "*.wav")

        if len(self.wav_file[0]) != 0:
            self.wav_filename = self.wav_file[0][0].split('/')[-1] # get the file name
            self.audio_path = self.wav_file[0]; # store path for next time
                
        if len(self.wav_file[0]) != 0:
            namelist = []
            for str in self.wav_file[0]:
                namelist.append(str.split('/')[-1])
            final_str = '\n'.join(namelist)
            selector_button.setText(final_str)
            selector_button.setProperty('filepath', self.wav_file)
    
    def keyPressEvent(self, event):
        """Key press event
        
        Connect enter key to next screen button
        
        """
        if event.key() == QtCore.Qt.Key_Enter or event.key() == QtCore.Qt.Key_Return:
            self.next_button_handler()

            
    def log_file_selector(self, selector_button):
        """Log file openner 
        
        Args:
            selector_button (QPushButton): Reference to QPushButton, used to change the text after an audio file is selected
        
        Raises:
            Exception: Subtitle file is invalid
        
        """
        # self.log_file is None open file directory at the current location
        # Else open at the previous directory
        if self.log_file != None:
            self.log_file = QtWidgets.QFileDialog.getOpenFileName(
                self, "Select log file", self.log_file[0], "(*.stm *.srt *.TextGrid *.sub *.txt *.vtt *.xml)")
        else:
            self.log_file = QtWidgets.QFileDialog.getOpenFileName(
                self, "Select log file", ".", "(*.stm *.srt *.TextGrid *.sub *.txt *.vtt *.xml)")
            
        self.log_filename = self.log_file[0].split('/')[-1]

        if self.log_file[0] != '':
            if self.log_filename.endswith('.stm', -4):
                try:
                    with open(self.log_file[0], encoding="utf-8") as logfile:
                        chatdata = logfile.read()
                        chatdata = chatdata.split('\n')
                        chatdata = chatdata[:len(chatdata) - 1]

                        for data in chatdata:
                            data = data.split(' ', 6)
                            if len(data) < 5:
                                raise Exception('Invalid log file')
                            starttime = float(data[3])
                            endtime = float(data[3])

                    selector_button.setText(self.log_filename)
                    selector_button.setProperty('filepath', self.log_file)
                except Exception:
                    self.window.statusbar.showMessage(
                        'Please provide a valid log file', 3000)
            elif self.log_filename.endswith('.srt', -4):
                try:
                    try:
                        subs = pysrt.open(self.log_file[0])
                    except UnicodeDecodeError:
                        subs = pysrt.open(
                            self.log_file[0], encoding='iso-8859-1')
                    selector_button.setText(self.log_filename)
                    selector_button.setProperty('filepath', self.log_file)
                except:
                    self.window.statusbar.showMessage(
                        'Please provide a valid log file here', 3000)
            elif self.log_filename.endswith('.TextGrid', -9):
                try:
                    grid = textgrids.TextGrid(self.log_file[0])
                    selector_button.setText(self.log_filename)
                    selector_button.setProperty('filepath', self.log_file)
                except:
                    self.window.statusbar.showMessage(
                        'Please provide a valid log file', 3000)
            elif self.log_filename.endswith('.sub', -4) or self.log_filename.endswith('.txt', -4) or self.log_filename.endswith('.vtt', -4) :
                try:
                    subs = pysubs2.load(self.log_file[0], encoding="utf-8")
                    selector_button.setText(self.log_filename)
                    selector_button.setProperty('filepath', self.log_file)
                except:
                    self.window.statusbar.showMessage(
                        'Please provide a valid log file', 3000)
            elif self.log_filename.endswith('.xml', -4):
                try:
                    root = ET.parse(self.log_file[0]).getroot()
                    selector_button.setText(self.log_filename)
                    selector_button.setProperty('filepath', self.log_file)
                except:
                    self.window.statusbar.showMessage(
                        'Please provide a valid log file', 3000)
               
    def restoremode_data(self):
        """Parse the subtitle files
        
        Return:
             speaker_names: Name of the speaker
             conversation_data: List of the transcript
             rootList: The xml root if the subtitle file format is xml
        
        """
        speaker_names = {}
        conversation_data = []
        rootList = {}
        for i in range(self.num_mics):
            path = self.inputs[i][4].property('filepath')[0]
            current_format = path.split('.')[-1]
            audio = self.inputs[i][3].property('filepath')[0]
            
            if current_format == 'stm':
                with open(path , encoding="utf-8") as logfile:
                    chatdata = logfile.read()
                    chatdata = chatdata.split('\n')
                    chatdata = chatdata[:len(
                        chatdata)-1] if chatdata[-1] == '' else chatdata[:len(chatdata)]
                    self.meetingname = chatdata[0].split(' ')[0]

                    for data in chatdata:
                        data = data + " "
                        match = re.search(self.regex_pattern, data)
                        device_id = match.group(2)
                        speaker_name = match.group(3)
                        start_time = match.group(4)
                        end_time = match.group(5)
                        speaker_message = match.group(10)
                        if speaker_message is None or speaker_message.strip() == "":
                            speaker_message = '--EMPTY--'
                        if speaker_names.get(speaker_name, None) is None:
                            speaker_names[speaker_name] = ['english', speaker_name, self.mic_ids[0],
                                                           audio, path, device_id, self.meetingname]
                        conversation_data.append(
                            [speaker_name, start_time, end_time, speaker_message, path ])
            
            if current_format == 'srt':
                try:
                    subs = pysrt.open(path)
                except:
                    subs = pysrt.open(path, encoding='iso-8859-1')
                for sub in subs:
                    filename = path.split('/')[-1][:-4]
                    if speaker_names.get(filename, None) is None:
                        speaker_names[filename] = ['english', filename, self.mic_ids[0],
                                                   audio, path, '0', filename]
                    start_time = str(sub.start.hours*3600 + sub.start.minutes * 60 + sub.start.seconds) + "." + str(sub.start.milliseconds)
                    end_time = str(sub.end.hours*3600 + sub.end.minutes * 60 + sub.end.seconds) + "." + str(sub.end.milliseconds)
                    conversation_data.append(
                        [filename, start_time, end_time, sub.text, path.split('/')[-1]])
            
            if current_format == 'TextGrid':
                grid = textgrids.TextGrid(path)
                filename = path.split('/')[-1][:-9]
                for index, speaker_name in enumerate(grid):
                    if speaker_names.get(speaker_name, None) is None:
                        speaker_names[speaker_name] = ['english', speaker_name, self.mic_ids[0],
                                                  audio, path, str(index), filename]
                    for data in grid[speaker_name]:
                        speaker_message = data.text
                        start_time = str(data.xmin)
                        end_time = str(data.xmax)
                        conversation_data.append(
                            [speaker_name, start_time, end_time, speaker_message, path.split('/')[-1]])
           
            if current_format == 'txt' or current_format == 'sub'  or current_format == 'vtt':
                subs = pysubs2.load(path, encoding="utf-8")
                filename = path.split('/')[-1][:-4]
                for sub in subs:        
                    if speaker_names.get(filename, None) is None:
                        speaker_names[filename] = ['english', filename, self.mic_ids[0],
                                                   audio, path, '0', filename]
                    start_time = str(sub.start/1000)
                    end_time = str(sub.end/1000)
                    conversation_data.append([filename, start_time, end_time, sub.text.replace('\\N','\n'),path.split('/')[-1]])
            
            if current_format == 'xml':
                root = ET.parse(path).getroot()
                rootList[path.split('/')[-1]] = root
                filename = path.split('/')[-1][:-4]
                for SegmentList in root:
                    # SpeechSegment = sentence
                    for SpeechSegment  in SegmentList:
                        speaker_name = SpeechSegment.attrib["spkrid"]
                        #speaker_names[speaker_name] = ['english', speaker_name, self.mic_ids[0],audio, path, '0', filename]
                        if speaker_names.get(speaker_name, None) is None:
                            speaker_names[speaker_name] = ['english', speaker_name, self.mic_ids[0], audio, path, '0', path]
                        
                        sentence = []
                        for Word in SpeechSegment:
                            sentence.append(Word.text+" ")
                        speaker_message = ''.join(sentence)
                        end_time = float(SpeechSegment.attrib["stime"]) + float(SpeechSegment.attrib["dur"])
                        end_time = format(end_time, '.2f')
                        end_time = str(end_time)
                        start_time = SpeechSegment.attrib["stime"]
                        conversation_data.append([speaker_name, start_time, end_time,speaker_message, path.split('/')[-1]])
        conversation_data = sorted(conversation_data, key=lambda x: float(x[1]))

        return speaker_names, conversation_data,rootList

    def asr_endpoint_selector(self, language, asr_endpoint):
        resample_rate = 8000 if asr_endpoint == '8khz' else 16000
        available_languages = self.window.available_languages_8k if asr_endpoint == '8khz' else self.window.available_languages_16k
        language.clear()
        for index, data in enumerate(available_languages):
            language.addItem(data)
            language.setItemData(
                index, data + '_' + str(resample_rate), QtCore.Qt.UserRole)
    def onCountChanged(self, value):
        self.progress.setValue(value)
    
    def audio_file_split_handler(self, selector_button):

        self.split_wav_file = QtWidgets.QFileDialog.getOpenFileNames(self, "Select wav file", ".", "*.wav")

        if len(self.split_wav_file[0]) != 0:
            self.split_wav_filename = self.split_wav_file[0][0].split('/')[-1] # get the file name
            self.split_audio_path = self.split_wav_file[0]; # store path for next time

        if len(self.split_wav_file[0]) != 0:
            namelist = []
            for stri in self.split_wav_file[0]:
                namelist.append(stri.split('/')[-1])
            final_str = '\n'.join(namelist)
            #selector_button.setText(final_str)
            selector_button.setProperty('filepath', self.split_wav_file)
        audioFile = self.split_audio_path[0]
        #print(type(self.split_audio_path[0][0]))
        numChannels = file_info.channels(audioFile)
        print(numChannels)
        for i in range(int(numChannels)):
            outputFile = final_str[:len(final_str)-4]+'channel-'+str(i+1)+'.wav'
            command = 'sox '+ audioFile + ' ' +  outputFile +  ' remix ' + str(i+1)
            print(command)
            os.system(command)

        
TIME_LIMIT = 100
class External(QThread):
    """
    Runs a counter thread.
    """
    countChanged = pyqtSignal(int)

    def run(self):
        count = 0
        while count < TIME_LIMIT:
            print(count)
            count +=10
            time.sleep(1)
            self.countChanged.emit(count)
            
