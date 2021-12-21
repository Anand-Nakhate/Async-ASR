import os
import sip
import queue
import wave
import urllib
import pyaudio
import shutil
import pysrt
import datetime
import configparser
import socket
import glob
import soundfile as sf
import pyqtgraph as pg
import numpy as np
import librosa
#import spacy 
import requests
import json
import re
import ctypes
import webcolors
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QTimer, QThread
from PyQt5.QtCore import pyqtSignal as SIGNAL
from PyQt5.QtGui import QBrush, QColor, QKeySequence
from threads.micthread import MicThread
from utilities.Customsignal import Customsignal
from utilities.CustomTable import CustomTableWidget
from utilities.NER_TableDialog import NER_TableDialog
from utilities.ModuleSeletorDialog import ModuleSeletorDialog
#from utilities.CustomTable1 import CustomTableWidget1
from requests_futures.sessions import FuturesSession
from threads.summary_thread import SummaryThread
from utilities.utils import timedelta_to_srt_timestamp, resource_path, write_to_textgrid, model_selector,cleanhtml,getColorCode,insert_str
import vlc
from utilities.CustomViewBox import CustomViewBox 
from slugify import slugify
from functools import partial
from utilities.asr import MyClient
from .customeditor import EditorDelegate
from threads.recordthread import RecordThread
from PyQt5.QtNetwork import QAbstractSocket
from .customtreeitem import CustomTreeWidgetItem
from .manage_speakers import Ui_manage_speakers_top_layout
from .labelledslider import LabelledSlider
from utilities.CustomDialog import Dialog 
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element, SubElement,Comment
from xml.dom import minidom
import threading
from timeit import default_timer as timer
from PyQt5.QtCore import pyqtSignal as Signal
import sys
sys.path.append('../')
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import QtCore, QtGui, QtWidgets
from screens.customeditor import EditorDelegate
import copy 

shared_FullData = {}

class Ui_fourth_screen(QtWidgets.QWidget):

    def __init__(self, window, mic_ids, meeting_name, num_mics, is_filemode=False, is_restoremode=False, convo_data=None, xmlRoot={},progress =None,prev_screen=None):
        QtWidgets.QWidget.__init__(self)
        self.window = window
        self.mic_ids = mic_ids
        self.meetingname = meeting_name
        self.num_mics = num_mics
        self.is_filemode = is_filemode
        self.is_restoremode = is_restoremode
        self.convo_data = convo_data
        self.prev_screen = prev_screen
        self.progress = progress
        self.sud_requests = queue.Queue()
        self.api_request = queue.Queue()
        self.failed = 0
        self.mic_threads = {}
        self.mic_status = {}
        self.color_mic_mapping = {}
        self.playback = {}
        self.record_threads = {}
        self.row_to_speaker_object = {}
        self.speaker_to_row = {}
        self.xmlRoot = xmlRoot
        self.reconnect_messages = {}
        self.sthreads = []
        self.playback_thread = []
        self.cacheAudio = {}

        self.colors = [(187, 216, 179, 100), (243, 182, 31, 100), (169, 159, 21, 100), (81, 13, 10, 100), (25, 17,
                                                                                                           2, 100), (208, 0, 0, 100), (63, 136, 197, 100), (3, 43, 67, 100), (19, 111, 99, 100), (237, 106, 94, 100)]
        self.autoloop = True
        self.summary_isVisible = False
        self.session_isPaused = False
        self.session_stopped = False
        self.log_saved = False

        self.current_media = None
        self.play_row = None
        self.current_play_rate = 1.0
        self.curr_position_slider = 0
        # self.offset = 0
        self.slider_start = 0
        self.remaining_time = 0
        self.set_pos_rem_time = -1

        self.ONE_MINUTE_RECORD_SIZE = 1860000 # Bytes

        self.config = configparser.ConfigParser()
        self.config.read(resource_path('services.ini'))
        self.config.read(resource_path('hotkey.ini'))
        self.config.read(resource_path('colorcode.ini'))

        self.model = None 
        
        self.summary_messages = ''
        self.summary_text = 'Fetching Summary!!!'
        self.log_path = 'recordings/' + self.meetingname + '/'

        self.icons = self.setup_icons()

        self.reconnect_icon = QtGui.QIcon()
        self.reconnect_icon.addPixmap(QtGui.QPixmap(resource_path(
            './icons/reconnect.png')), QtGui.QIcon.Normal, QtGui.QIcon.Off)

        self.disconnect_icon = QtGui.QIcon()
        self.disconnect_icon.addPixmap(QtGui.QPixmap(resource_path(
            './icons/disconnect.png')), QtGui.QIcon.Normal, QtGui.QIcon.Off)

        self.assign_icon = QtGui.QIcon()
        self.assign_icon.addPixmap(QtGui.QPixmap(resource_path(
            './icons/assign.png')), QtGui.QIcon.Normal, QtGui.QIcon.Off)

        self.req_session = FuturesSession()
        self.req_api_session = FuturesSession()
        self.vlc_instance = vlc.Instance()
        self.vlc_mediaplayer = self.vlc_instance.media_player_new()
        
        # process api request
        self.api_timer = QTimer()
        self.api_timer.timeout.connect(self.api_response_handler)
        self.api_data = {}
        self.api_counter = 0;
        
        self.sud_timer = QTimer()
        self.player_timer = QTimer()
        self.slider_timer = QTimer()
        self.record_time_remaining_timer = QTimer()
        self.record_time_remaining_timer.setInterval(60000)
        self.record_time_remaining_timer.timeout.connect(self.update_remaining_record_time)
        self.slider_timer.setInterval(10)
        self.slider_timer.timeout.connect(self.update_slider_ui)
        self.player_timer.setSingleShot(True)
        self.player_timer.timeout.connect(self.stop_playback)

        self.window.closeEvent = self.closeEvent

        self.customsignal = Customsignal()
        self.customsignal.add_message.connect(self.add_message)
        self.customsignal.update_message.connect(self.update_message)
        self.customsignal.update_summary.connect(self.update_summary)
        self.customsignal.reconnect_websocket.connect(self.reconnect_button_handler)
        self.customsignal.update_treeitem_background.connect(self.update_treeitem_background)
        self.customsignal.terminate_thread.connect(self.terminate_thread)
        self.customsignal.stop_signal.connect(self.stop_playback_2)
        self.customsignal.start_signal.connect(self.playbackaudio)
        self.customsignal.start_recording.connect(self.start_recording)
        self.customsignal.update_speakers.connect(self.update_speakers)
        self.customsignal.delete_speakers.connect(self.delete_speakers)
        self.customsignal.assign_speakers.connect(self.assign_speakers)
        
        self.sud_timer.timeout.connect(self.sud_thread)

        self.clickFromWf = False
        self.timer=QTimer()
        self.timer.timeout.connect(self.showTime)
        self.vb = CustomViewBox()
        self.gv = pg.GraphicsView()
        self.proxy = pg.SignalProxy(self.vb.sigMousePressed,rateLimit = 0, slot=self.mouseclick)
        self.samplerate = 0
        
        # module_row_numbers-> Key: Module Name;  Value: Row Numbers corresponding to that module
        self.modules = ["NER", "Sound", "Event"]
        self.module_row_numbers = {}
        self.module_row_numbers["NER"] = [1, 3]
        self.module_row_numbers["Sound"] = [2, 4]
        self.module_row_numbers["Event"] = [1, 2, 3, 4]

        
        # self.test = QTimer()
        # self.test.timeout.connect(self.pause_button_handler)
        # self.test.start(11000)
    def showTime(self):
        #self.vb.setRange(rect=None, xRange=[self.counter-30000,self.counter+80000], yRange=None, padding=None, update=True, disableAutoRange=True)
        if self.vlc_mediaplayer.is_playing():
            time  = self.vlc_mediaplayer.get_time()
            if time != 0:
                self.vb.removeItem(self.p2)
                self.p2 = pg.InfiniteLine(time*(self.samplerate/1000) + self.offset*self.samplerate)
                self.vb.addItem(self.p2)
                
            
    
    def mouseclick(self, evt): 
        self.xPos = mousePoint = evt[0].x()
        self.clickFromWf = True
        if self.session_stopped or self.is_restoremode or self.is_filemode:
            self.playaudio_button.show()
            self.stopaudio_button.show()
            self.increaserate_button.show()
            self.currentrate_button.show()
            self.decreaserate_button.show()
            self.positionslider.show()
        
        self.playbackaudio()

        
    def startTimer(self):
        self.timer.start(10)
            
    def closeEvent(self, event):
        if not self.log_saved:
            msg = QtWidgets.QMessageBox(self)
            msg.setIcon(QtWidgets.QMessageBox.Question)
            msg.setWindowTitle('Window Close')
            msg.setText(
                "Caution: You haven't saved logs for the session, it is recommended that you save the logs.")
            save_and_exit = msg.addButton(
                'Save and exit', QtWidgets.QMessageBox.AcceptRole)
            exit_application = msg.addButton(
                'Exit', QtWidgets.QMessageBox.RejectRole)
            cancel_action = msg.addButton(
                'Cancel', QtWidgets.QMessageBox.RejectRole)
            msg.setWindowFlags(msg.windowFlags() |
                               QtCore.Qt.CustomizeWindowHint)
            msg.setWindowFlag(QtCore.Qt.WindowCloseButtonHint, False)
            msg.setDefaultButton(save_and_exit)
            msg.exec_()
            msg.deleteLater()

            for playthread in self.playback_thread:
                playthread.wait(2000)

            if msg.clickedButton() is save_and_exit:
                self.log_button_handler(False, event)
            if msg.clickedButton() is exit_application:
                event.accept()
            if msg.clickedButton() is cancel_action:
                event.ignore()

    def terminate_thread(self, thread):
        thread.wait(1000)

    def setupUi(self):
        """Setup the UI
        
        This method need to be called after the class has been instantiated. This method will create the GUI for
        our window.
    
            
        """
        self.setObjectName("fourth_screen")
        self.resize(800, 700)
        self.verticalLayout = QtWidgets.QVBoxLayout(self)
        self.verticalLayout.setObjectName("verticalLayout")

        self.meetinginfo_layout = QtWidgets.QHBoxLayout()
        self.meetinginfo_layout.setObjectName("meetinginfo_layout")
        self.meeting_name = QtWidgets.QLabel(self)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.meeting_name.sizePolicy().hasHeightForWidth())
        self.meeting_name.setSizePolicy(sizePolicy)
        self.meeting_name.setAlignment(
            QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.meeting_name.setObjectName("meeting_name")
        self.meetinginfo_layout.addWidget(self.meeting_name)
        self.meeting_status = QtWidgets.QLabel(self)
        self.meeting_status.setObjectName("meeting_status")
        self.meetinginfo_layout.addWidget(self.meeting_status)

        self.verticalLayout.addLayout(self.meetinginfo_layout)

        ## Graph waveform start
        self.vb.setMouseEnabled(x=True, y=False)
        self.l = QtGui.QGraphicsGridLayout()     
        self.l.addItem(self.vb, 0, 1)
        self.xScale = pg.AxisItem(orientation='bottom', linkView=self.vb)
        self.l.addItem(self.xScale, 1, 1)
        self.yScale = pg.AxisItem(orientation='left', linkView=self.vb)
        self.l.addItem(self.yScale, 0, 0)
        self.gv.setMaximumHeight (250)
        self.gv.enableMouse(False)
        self.gv.centralWidget.setLayout(self.l)
        self.verticalLayout.addWidget(self.gv)
        # Graph waveform end

        
        self.H_layout = QtWidgets.QHBoxLayout()
        
        self.tables_layout = QtWidgets.QVBoxLayout()
        self.tables_layout.setObjectName("tables_layout")

        self.speaker_legend = QtWidgets.QTreeWidget(self)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.speaker_legend.sizePolicy().hasHeightForWidth())
        self.speaker_legend.setSizePolicy(sizePolicy)
        self.speaker_legend.setMaximumSize(QtCore.QSize(176, 100))
        self.speaker_legend.setObjectName("speaker_legend")
        font = QtGui.QFont()
        font.setPointSize(14)
        self.speaker_legend.headerItem().setFont(0, font)
        self.speaker_legend.setColumnCount(2)
        self.speaker_legend.header().setStretchLastSection(True)
        self.speaker_legend.header().setSectionResizeMode(
            0, QtWidgets.QHeaderView.ResizeToContents)
        self.speaker_legend.header().setSectionResizeMode(
            1, QtWidgets.QHeaderView.Stretch)
        self.speaker_legend.setMaximumSize(QtCore.QSize(275, 16777215))
        self.speaker_legend.setHeaderHidden(True)
        self.icon = QtGui.QIcon()
        self.icon.addPixmap(QtGui.QPixmap(resource_path("./icons/userone.png")),
                            QtGui.QIcon.Normal, QtGui.QIcon.Off)

        self.tables_layout.addWidget(self.speaker_legend)
        
        # self.testing = QtWidgets.QTreeWidget(self)
        # self.testing.setMaximumSize(QtCore.QSize(246, 200))
        # self.testing.setHeaderHidden(True)
        
        self.ColorCodeTable =  QtWidgets.QTableWidget(self)
        self.ColorCodeTable.setMaximumSize(QtCore.QSize(275, 255))
        self.ColorCodeTable.setColumnCount(2)
        self.ColorCodeTable.horizontalHeader().setStretchLastSection(True)
        self.ColorCodeTable.verticalHeader().setVisible(False)
        item = QtWidgets.QTableWidgetItem()
        item.setText("Entity")
        self.ColorCodeTable.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        item.setText("Color")
        self.ColorCodeTable.setHorizontalHeaderItem(1, item)
        self.ColorCodeTable.setColumnWidth(0,175)
        self.ColorCodeTable.setColumnWidth(1,80)
        # self.testing.setHeaderHidden(True)
        
        self.tables_layout.addWidget(self.ColorCodeTable)
        
        
        
        
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        
        #Table show entries and Page jump
        self.TopHlayout = QtWidgets.QHBoxLayout()
        self.showEntries = QtWidgets.QLabel()
        self.showEntries.setText("Show")
        self.showEntries.setFont(QtGui.QFont("MS Shell Dlg 2",10))
        self.showEntries2 = QtWidgets.QLabel()
        self.showEntries2.setText("entries")
        self.showEntries2.setFont(QtGui.QFont("MS Shell Dlg 2",10))
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
        self.jumpLabel.setFont(QtGui.QFont("MS Shell Dlg 2",10))

        self.txtPage = QtWidgets.QLineEdit()
        self.txtPage.setFixedWidth(100)
        self.txtPage.setText("")
        self.txtPage.setValidator(QtGui.QIntValidator(1, 13999999))
        self.txtPage.textEdited.connect(self.PageJump)
        self.TopHlayout.addWidget(self.jumpLabel)
        self.TopHlayout.addWidget(self.txtPage)
        self.verticalLayout_2.addLayout(self.TopHlayout)
        # End of Table show entries and Page jump
        
        self.conversation_table = CustomTableWidget()
        self.conversation_table.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.conversation_table.customContextMenuRequested.connect(self.generateMenu)
        self.conversation_table.viewport().installEventFilter(self)
        self.PageNumberList = QtWidgets.QListWidget()
        self.PageNumberList.viewport().setAutoFillBackground( False )
        self.PageNumberList.setFlow(QtWidgets.QListView.LeftToRight) 
        self.PageNumberList.setFixedHeight(40)
        self.PageNumberList.itemClicked.connect(self.ListItemClicked)
        self.conversation_table.setpageListWidget(self.PageNumberList)
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
        self.conversation_table.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.conversation_table.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
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
        if not self.is_restoremode:
            self.conversation_table.setItemDelegateForColumn(2, EditorDelegate(self, self.customsignal))
        else:
            self.conversation_table.setItemDelegateForColumn(3, EditorDelegate(self, self.customsignal))
        self.verticalLayout_2.addWidget(self.conversation_table)
        
        # paging 
        self.Hlayout = QtWidgets.QHBoxLayout()
        
        self.next = QtWidgets.QPushButton()
        self.next.clicked.connect(self.nextButton)   
        self.next.setFixedWidth(25) 
        self.next.setFixedHeight(42) 
        self.next.setIcon(QtGui.QIcon("./icons/right.png"))
        
        self.prev = QtWidgets.QPushButton()
        self.prev.clicked.connect(self.prevButton)  
        self.prev.setIcon(QtGui.QIcon("./icons/left.png"))
        self.prev.setFixedWidth(25) 
        self.prev.setFixedHeight(42) 
        
        self.skipFirst = QtWidgets.QPushButton()
        self.skipFirst.clicked.connect(self.skipFirst_handler)   
        self.skipFirst.setFixedWidth(30) 
        self.skipFirst.setFixedHeight(42) 
        self.skipFirst.setIcon(QtGui.QIcon("./icons/skipFirst.png"))
        
        self.skipLast = QtWidgets.QPushButton()
        self.skipLast.clicked.connect(self.skipLast_handler)  
        self.skipLast.setIcon(QtGui.QIcon("./icons/skipLast.png"))
        self.skipLast.setFixedWidth(30) 
        self.skipLast.setFixedHeight(42) 
        
        self.Hlayout.addWidget(self.skipFirst)
        self.Hlayout.addWidget(self.prev)
        self.Hlayout.addWidget(self.PageNumberList)
        self.Hlayout.addWidget(self.next)
        self.Hlayout.addWidget(self.skipLast)
    
        self.Hlayout.setContentsMargins(QtCore.QMargins(0,0,0,0))
        self.Hlayout.setSpacing(0)

        self.verticalLayout_2.addLayout(self.Hlayout)
        #self.verticalLayout_2.addWidget(self.PageNumberList)

        self.summary_label = QtWidgets.QLabel(self)
        self.summary_label.setObjectName("summary_label")

        self.verticalLayout_2.addWidget(self.summary_label)

        self.summary_box = QtWidgets.QTextEdit(self)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.summary_box.sizePolicy().hasHeightForWidth())
        self.summary_box.setSizePolicy(sizePolicy)
        self.summary_box.setMinimumSize(QtCore.QSize(0, 0))
        self.summary_box.setObjectName("summary_box")

        self.verticalLayout_2.addWidget(self.summary_box)
        self.H_layout.addLayout(self.tables_layout)
        self.H_layout.addLayout(self.verticalLayout_2)

        self.verticalLayout.addLayout(self.H_layout)

        self.slider_layout = QtWidgets.QHBoxLayout()
        if not self.is_filemode and not self.is_restoremode:
            self.remaining_record_time = QtWidgets.QLabel(self)
            self.remaining_record_time.setObjectName("remaining_record_time")
            hours_available, minutes_available = self.get_recording_time_remaining()
            self.remaining_record_time.setText("Remaining Record Time: " + str(hours_available) + " hours " + str(minutes_available) + " min")
            self.slider_layout.addWidget(self.remaining_record_time)

        self.slider_layout.insertStretch(0)
        self.positionslider = LabelledSlider()
        self.positionslider.sl.mousePressEvent = self.set_position
        self.positionslider.sl.mouseMoveEvent = self.set_position
        self.slider_layout.addWidget(self.positionslider)

        self.autoplay_checkbox = QtWidgets.QCheckBox(self)
        self.autoplay_checkbox.setChecked(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.autoplay_checkbox.sizePolicy().hasHeightForWidth())
        self.autoplay_checkbox.setSizePolicy(sizePolicy)
        self.autoplay_checkbox.setObjectName("autoplay_checkbox")
        self.slider_layout.addWidget(self.autoplay_checkbox)

        self.autoLoop_checkbox = QtWidgets.QCheckBox(self)
        self.autoLoop_checkbox.setChecked(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.autoLoop_checkbox.sizePolicy().hasHeightForWidth())
        self.autoLoop_checkbox.setSizePolicy(sizePolicy)
        self.autoLoop_checkbox.setObjectName("autoLoop_checkbox")

        self.slider_layout.addWidget(self.autoLoop_checkbox)

        self.slider_layout.addStretch()

        self.verticalLayout.addLayout(self.slider_layout)

        self.buttons_layout = QtWidgets.QHBoxLayout()
        # self.buttons_layout.setContentsMargins(550, -1, 550, -1)
        self.buttons_layout.insertStretch(0)
        self.buttons_layout.setSpacing(6)
        self.buttons_layout.setObjectName("buttons_layout")

        self.prevscreen_button = QtWidgets.QPushButton(self)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.prevscreen_button.sizePolicy().hasHeightForWidth())
        self.prevscreen_button.setSizePolicy(sizePolicy)
        self.prevscreen_button.setObjectName("prevscreen_button")
        self.buttons_layout.addWidget(self.prevscreen_button)

        self.managespeakers_button = QtWidgets.QPushButton(self)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.managespeakers_button.sizePolicy().hasHeightForWidth())
        self.managespeakers_button.setSizePolicy(sizePolicy)
        self.managespeakers_button.setObjectName("managespeakers_button")
        self.buttons_layout.addWidget(self.managespeakers_button)

        self.record_button = QtWidgets.QPushButton(self)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.record_button.sizePolicy().hasHeightForWidth())
        self.record_button.setSizePolicy(sizePolicy)
        self.record_button.setObjectName("record_button")
        self.buttons_layout.addWidget(self.record_button)

        self.module_button = QtWidgets.QPushButton(self)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.module_button.sizePolicy().hasHeightForWidth())
        self.module_button.setSizePolicy(sizePolicy)
        self.module_button.setObjectName("module_button")
        self.buttons_layout.addWidget(self.module_button)

        self.ner_button = QtWidgets.QPushButton(self)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.ner_button.sizePolicy().hasHeightForWidth())
        self.ner_button.setSizePolicy(sizePolicy)
        self.ner_button.setObjectName("ner_button")
        self.buttons_layout.addWidget(self.ner_button)

        self.stop_button = QtWidgets.QPushButton(self)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.stop_button.sizePolicy().hasHeightForWidth())
        self.stop_button.setSizePolicy(sizePolicy)
        self.stop_button.setObjectName("stop_button")
        self.buttons_layout.addWidget(self.stop_button)

        self.pause_button = QtWidgets.QPushButton(self)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.pause_button.sizePolicy().hasHeightForWidth())
        self.pause_button.setSizePolicy(sizePolicy)
        self.pause_button.setObjectName("pause_button")
        self.buttons_layout.addWidget(self.pause_button)

        self.log_button = QtWidgets.QPushButton(self)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.log_button.sizePolicy().hasHeightForWidth())
        self.log_button.setSizePolicy(sizePolicy)
        self.log_button.setObjectName("log_button")
        self.buttons_layout.addWidget(self.log_button)

        self.playaudio_button = QtWidgets.QPushButton(self)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.playaudio_button.sizePolicy().hasHeightForWidth())
        self.playaudio_button.setSizePolicy(sizePolicy)
        self.playaudio_button.setObjectName("playaudio_button")
        self.buttons_layout.addWidget(self.playaudio_button)

        self.stopaudio_button = QtWidgets.QPushButton(self)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.stopaudio_button.sizePolicy().hasHeightForWidth())
        self.stopaudio_button.setSizePolicy(sizePolicy)
        self.stopaudio_button.setObjectName("stopaudio_button")
        self.buttons_layout.addWidget(self.stopaudio_button)

        self.decreaserate_button = QtWidgets.QPushButton(self)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.decreaserate_button.sizePolicy().hasHeightForWidth())
        self.decreaserate_button.setSizePolicy(sizePolicy)
        self.decreaserate_button.setObjectName("decreaserate_button")
        self.buttons_layout.addWidget(self.decreaserate_button)

        self.currentrate_button = QtWidgets.QPushButton(self)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.currentrate_button.sizePolicy().hasHeightForWidth())
        self.currentrate_button.setSizePolicy(sizePolicy)
        self.currentrate_button.setObjectName("currentrate_button")
        self.buttons_layout.addWidget(self.currentrate_button)

        self.increaserate_button = QtWidgets.QPushButton(self)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.increaserate_button.sizePolicy().hasHeightForWidth())
        self.increaserate_button.setSizePolicy(sizePolicy)
        self.increaserate_button.setObjectName("increaserate_button")
        self.buttons_layout.addWidget(self.increaserate_button)

        self.summary_button = QtWidgets.QPushButton(self)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.summary_button.sizePolicy().hasHeightForWidth())
        self.summary_button.setSizePolicy(sizePolicy)
        self.summary_button.setObjectName("summary_button")
        self.buttons_layout.addWidget(self.summary_button)

        self.verticalLayout.addLayout(self.buttons_layout)
        self.buttons_layout.addStretch()

        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)

        self.stop_button.hide()
        self.pause_button.hide()
        self.log_button.hide()
        self.summary_button.hide()
        self.summary_label.hide()
        self.summary_box.hide()
        self.playaudio_button.hide()
        self.stopaudio_button.hide()
        self.managespeakers_button.hide()
        self.increaserate_button.hide()
        self.currentrate_button.hide()
        self.decreaserate_button.hide()
        self.positionslider.hide()

        if self.is_restoremode:
            self.record_button.hide()
            self.log_button.show()
            # self.summary_button.show() # uncomment when summary feature is stable

        self.record_button.clicked.connect(self.record_button_handler)
        self.stop_button.clicked.connect(self.stop_button_handler)
        self.pause_button.clicked.connect(self.pause_button_handler)
        self.log_button.clicked.connect(self.log_button_handler)
        self.summary_button.clicked.connect(self.summary_button_handler)
        self.playaudio_button.clicked.connect(self.playbackaudio)
        self.stopaudio_button.clicked.connect(self.stop_playback_2)
        self.prevscreen_button.clicked.connect(self.prevscreen_handler)
        self.increaserate_button.clicked.connect(self.increase_playrate)
        self.decreaserate_button.clicked.connect(self.decrease_playrate)
        self.currentrate_button.clicked.connect(self.reset_currentrate)
        self.managespeakers_button.clicked.connect(self.managespeakers)
        self.module_button.clicked.connect(self.select_module_handler)
        self.ner_button.clicked.connect(self.NER_module_table_handler)
        #self.module_button.clicked.connect(self.conversation_table_custom_handler)
        # selectionModel = self.conversation_table.selectionModel()
        # selectionModel.selectionChanged.connect(self.enable_change_speakers)

        self.conversation_table.currentItemChanged.connect(self.enable_change_speakers)

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.window.setWindowTitle(_translate(
            "ASR - Session", "ASR - Session"))

        self.meeting_name.setText(_translate(
            "fourth_screen", self.meetingname + " -"))
        self.meeting_status.setText(_translate("fourth_screen", "Status"))

        __sortingEnabled = self.speaker_legend.isSortingEnabled()
        self.speaker_legend.setSortingEnabled(False)
        self.speaker_legend.setSortingEnabled(__sortingEnabled)

        item = self.conversation_table.horizontalHeaderItem(0)
        item.setText(_translate("fourth_screen", "Speakers"))
        item = self.conversation_table.horizontalHeaderItem(1)
        item.setText(_translate("fourth_screen", "Timestamp"))
        item = self.conversation_table.horizontalHeaderItem(2)
        item.setText(_translate("fourth_screen", "Messages"))
        __sortingEnabled = self.conversation_table.isSortingEnabled()
        self.conversation_table.setSortingEnabled(False)
        self.conversation_table.setSortingEnabled(__sortingEnabled)

        self.summary_label.setText(_translate("fourth_screen", "Summary"))
        self.record_button.setText(_translate("fourth_screen", "Record"))
        self.stop_button.setText(_translate("fourth_screen", "Stop"))
        self.pause_button.setText(_translate("fourth_screen", "Pause"))
        self.log_button.setText(_translate("fourth_screen", "Save Logs"))
        self.summary_button.setText(_translate("fourth_screen", "Summary"))
        self.playaudio_button.setText(_translate("fourth_screen", "Play"))
        self.stopaudio_button.setText(_translate("fourth_screen", "Stop"))
        self.prevscreen_button.setText(_translate("fourth_screen", "Back"))
        self.increaserate_button.setText(_translate("fourth_screen", "+"))
        self.decreaserate_button.setText(_translate("fourth_screen", "-"))
        self.autoplay_checkbox.setText(_translate("fourth_screen", "Autoplay Transcript"))
        self.autoLoop_checkbox.setText(_translate("fourth_screen", "Auto Loop"))
        self.currentrate_button.setText(_translate("fourth_screen", str(self.current_play_rate)))
        self.managespeakers_button.setText(_translate("fourth_screen", 'Change Speaker'))
        self.module_button.setText(_translate(
            "fourth_screen", "Module Analyzer"))
        self.ner_button.setText(_translate(
            "fourth_screen", "NER"))
        self.hotkeyDict = {}
        self.buildColorTable()
        QtWidgets.QShortcut(QKeySequence(self.config["HOTKEY"]["EnterexitEdit"]), self.conversation_table,
                            self.handle_enter, context=QtCore.Qt.WidgetShortcut)
        # QtWidgets.QShortcut(QKeySequence(self.config["HOTKEY"]["EnterexitEdit"]), self.conversation_table,
        #                     self.handle_enter, context=QtCore.Qt.WidgetShortcut)
        self.hotkeyDict["restartplay"] = QtWidgets.QShortcut(QKeySequence(self.config["HOTKEY"]["restartplay"]), self.conversation_table,
                            self.restart_playback, context=QtCore.Qt.WidgetWithChildrenShortcut)
        self.hotkeyDict["play"] = QtWidgets.QShortcut(QKeySequence(self.config["HOTKEY"]["play"]), self.conversation_table,
                            self.playbackaudio, context=QtCore.Qt.WidgetWithChildrenShortcut)
        self.hotkeyDict["decreaseplayrate"] = QtWidgets.QShortcut(QKeySequence(self.config["HOTKEY"]["decreaseplayrate"]), self.conversation_table,
                            self.decrease_playrate, context=QtCore.Qt.WidgetWithChildrenShortcut)
        self.hotkeyDict["increaseplayrate"] = QtWidgets.QShortcut(QKeySequence(self.config["HOTKEY"]["increaseplayrate"]), self.conversation_table,
                            self.increase_playrate, context=QtCore.Qt.WidgetWithChildrenShortcut)
        self.hotkeyDict["resetplayrate"] = QtWidgets.QShortcut(QKeySequence(self.config["HOTKEY"]["resetplayrate"]), self.conversation_table,
                            self.reset_currentrate, context=QtCore.Qt.WidgetWithChildrenShortcut)
        QtWidgets.QShortcut(QKeySequence("Tab"), self.conversation_table,
                            self.playbackaudio, context=QtCore.Qt.WidgetWithChildrenShortcut)
        QtWidgets.QShortcut(QKeySequence(self.config["HOTKEY"]["delete"]), self.conversation_table,
                            self.delete_transcript, context=QtCore.Qt.WidgetShortcut)
        self.hotkeyDict["autoloop"] =  QtWidgets.QShortcut(QKeySequence(self.config["HOTKEY"]["autoloop"]), self.conversation_table,
                            self.toggleAutoLoop, context=QtCore.Qt.WidgetWithChildrenShortcut)
        self.hotkeyDict["searchpage"] = QtWidgets.QShortcut(QKeySequence(self.config["HOTKEY"]["searchpage"]), self.conversation_table,
                            self.focusTextBox, context=QtCore.Qt.WidgetWithChildrenShortcut)
        if self.is_restoremode:
            self.restore_legend(self.mic_ids)

            self.conversation_table.horizontalHeader().setSectionResizeMode(
                2, QtWidgets.QHeaderView.ResizeToContents)

            self.restore_table(self.mic_ids, self.convo_data)
            
            self.log_path = 'recordings/' + self.meeting_name.text().strip()
            for mic in self.mic_ids:
                self.playback[mic] = self.mic_ids[mic][3]
            self.conversation_table.hideColumn(4)
            # data_x = []
            # for mic in self.mic_ids:
            #     for wav in self.mic_ids[mic][3]:
            #         x, sr = librosa.load(wav, sr =16000)
            #         data_x.append(x)
            
            # x = []
            # for array in data_x:
            #     x = np.concatenate((x, array))

            # self.p1 = pg.PlotDataItem()
            # self.p1.setData(y=x, x=np.arange(0, len(x)))
            # self.vb.addItem(self.p1)
            # self.p2 = pg.InfiniteLine(0)
            # self.vb.addItem(self.p2)
            return
        else:
            self.conversation_table.hideColumn(4)
        self.speaker_legend.headerItem().setText(1, _translate("fourth_screen", "Meeting Speakers"))
        self.conversation_table.hideColumn(3)
        self.setup_speaker_legend()

    def prevscreen_handler(self):
        self.window.centralwidget.setCurrentWidget(self.prev_screen)
        self.window.showNormal()
        self.window.centralwidget.adjustSize()

    def handle_enter(self):
        self.conversation_table.editItem(self.conversation_table.currentItem())

    def toggleAutoLoop(self):	
        if self.autoLoop_checkbox.isChecked():
            self.autoLoop_checkbox.setChecked(False)
        else:
            self.autoLoop_checkbox.setChecked(True)

    def restart_playback(self):
        self.vlc_mediaplayer.stop()
        self.playbackaudio()

    def stop_playback_2(self):
        """Stop the playback
        
        The different between stop_playback and this method is that this method will stop the playback
        entirely without audio looping 
        
        """
        self.positionslider.sl.setValue(0)
        self.curr_position_slider = self.slider_start
        self.vlc_mediaplayer.stop()
        self.slider_timer.stop()
        self.timer.stop()
        self.playaudio_button.setText('Play')
        self.set_pos_rem_time = -1
        
        # Reset the InfiniteLine
        self.removeGraphItem("InfiniteLine")
        self.p2 = pg.InfiniteLine(0)
        self.vb.addItem(self.p2)
        
        
        self.autoloop = False

    def stop_playback(self):
        """Stop the playback
        
        The different between stop_playback_2 and this method is that this method will auto loop back the audio
        
        """
        self.positionslider.sl.setValue(0)
        self.curr_position_slider = self.slider_start
        self.vlc_mediaplayer.stop()
        self.slider_timer.stop()
        self.timer.stop()
        self.playaudio_button.setText('Play')
        self.set_pos_rem_time = -1
        
        # Reset the InfiniteLine
        self.removeGraphItem("InfiniteLine")
        self.p2 = pg.InfiniteLine(0)
        self.vb.addItem(self.p2)
        
        # If autoloop checkbox is checked then play the audio again
        if self.autoLoop_checkbox.isChecked() and self.autoloop == True:
           self.playbackaudio()
           return
    def playbackaudio(self):
        """Start the audio playback
        
        return is row is -1 (no row is selected)
        
        Note: restoremode and filemode have different columns hence there is 2 different ways to retreive the
        start time and end time
        
        """
        if (self.session_stopped or self.is_restoremode or self.is_filemode) and ( len(self.conversation_table.selectionModel().selectedRows()) == 1 or self.clickFromWf):
            self.autoloop = True
            # If user clicks on the waveform.
            # As the waveform is not associate to any row, we retreive the row index based on the selected time
            if self.clickFromWf:
                sec = self.xPos/self.samplerate
                totalrow = self.conversation_table.rowCount()
                row = -1
                if self.is_restoremode:
                    for i in range(totalrow):
                        start_time = float(self.conversation_table.item(i, 1).text().strip())
                        end_time = float(self.conversation_table.item(i, 2).text().strip())
                        if sec >start_time and sec < end_time:
                            row = i
                            self.conversation_table.selectRow(i)
                            self.curr_position_slider = start_time * 1000
                            break
                elif self.samplerate != 0 :
                    for i in range(totalrow):
                        start_time, end_time = self.conversation_table.item(i, 3).text().strip().split(':')
                        if sec >float(start_time) and sec < float(end_time):
                            row = i
                            self.conversation_table.selectRow(i)
                            self.curr_position_slider = (float(start_time)) * 1000
                            break                    
            else:
                row = self.conversation_table.currentRow()
            
            # No row, return
            if row == -1:
                return
            
            micid, speakername = self.conversation_table.item(row, 0).data(QtCore.Qt.UserRole).split(':')

            if self.is_restoremode:
                start_time = self.conversation_table.item(row, 1).text().strip()
                end_time = self.conversation_table.item(row, 2).text().strip()
            else:
                try:
                    start_time, end_time = self.conversation_table.item(row, 3).text().strip().split(':')
                except:
                    return
            
            # Calculate the start/end time based on where the user clicks on the waveform 
            if(self.vb.oldX !=None):
                start_time = self.vb.oldX[0]/self.samplerate
                end_time = self.vb.oldX[1]/self.samplerate
                self.curr_position_slider = (float(start_time)) * 1000
                
            start_time = (float(start_time)) * 1000  # milliseconds
            end_time = (float(end_time)) * 1000  # milliseconds
            micid_speaker = micid if (self.session_stopped or self.is_filemode) else speakername
            self.duration = end_time - start_time
            self.slider_start = start_time

            if row == self.play_row and self.vlc_mediaplayer.is_playing() == 1:
                self.slider_timer.stop()
                self.remaining_time = self.player_timer.remainingTime()
                self.player_timer.stop()
                self.vlc_mediaplayer.pause()
                self.playaudio_button.setText('Play')
                return

            if row == self.play_row and self.vlc_mediaplayer.is_playing() == 0 and self.vlc_mediaplayer.get_time() != -1:
                self.player_timer.start(self.remaining_time)
                self.slider_timer.start()
                self.vlc_mediaplayer.play()
                self.playaudio_button.setText('Pause')
                return

            self.player_timer.stop()
            
            
            #self.clipToPlay(self.curr_position_slider,micid_speaker)
            #choose which audio file to play as we allow user to choose multiple  audio files
            clip, offset =  self.clipToPlay(start_time/1000 ,micid_speaker)
            self.current_media = self.vlc_instance.media_new(clip)
            self.vlc_mediaplayer.set_media(self.current_media)
            #self.vlc_instance.vlm_set_loop(clip.split('.')[0], True) 
            self.vlc_mediaplayer.play()
            
            self.a =  round(float(self.curr_position_slider - offset * 1000))
            self.vlc_mediaplayer.set_time(self.a)
            if self.clickFromWf:
                self.vlc_mediaplayer.set_time(int(sec*1000))

            self.vlc_mediaplayer.set_rate(self.current_play_rate)
            if self.clickFromWf:
                self.remaining_time = ( end_time - int(sec*1000)) / self.current_play_rate
            else:
                self.remaining_time = self.duration / self.current_play_rate

            if self.set_pos_rem_time != -1:
                self.player_timer.start(self.set_pos_rem_time)
            else:
                self.player_timer.start(self.remaining_time)
            label_range = range(0, int(self.duration/1000)+1, 1)
            self.positionslider.levels = list(zip(label_range, map(str, label_range)))
            self.positionslider.sl.setMaximum(int(self.duration/1000))
            self.positionslider.update()
            self.slider_timer.start()
            self.startTimer()
            self.play_row = row
            self.playaudio_button.setText('Pause')
            
            self.clickFromWf = False


    def clipToPlay(self,startTime,micid_speaker):
        total_time = 0
        preTotal_time = 0
        for i in range(len(self.playback[micid_speaker])):
            if self.playback[micid_speaker][i] in self.cacheAudio:
                f = self.cacheAudio[self.playback[micid_speaker][i]]
                # print("Cached")
            else:
                f = sf.SoundFile(self.playback[micid_speaker][i])
                self.cacheAudio[self.playback[micid_speaker][i]] = f
            self.samplerate = f.samplerate
            time = (len(f) / f.samplerate)
            f.close()
            preTotal_time = total_time
            total_time = time + total_time
            if startTime<total_time:
                return self.playback[micid_speaker][i] , preTotal_time
        
    
    def restore_legend(self, speaker_names):
        for index, name in enumerate(speaker_names):
            item_0 = CustomTreeWidgetItem(
                self.speaker_legend, customsignal=self.customsignal)
            item_0.setFlags(item_0.flags() | QtCore.Qt.ItemIsEditable)
            item_0.setText(1, name)
            font = QtGui.QFont()
            font.setPointSize(15)
            item_0.setFont(1, font)
            item_0.setIcon(1, self.icons[index])
            item_0.setBackground(1, QBrush(QColor(
                self.colors[index][0], self.colors[index][1], self.colors[index][2], self.colors[index][3])))

            assign_button = QtWidgets.QPushButton()
            assign_button.setObjectName("assign_button")
            assign_button.setGeometry(QtCore.QRect(500, 30, 211, 131))
            assign_button.setIcon(self.assign_icon)
            assign_button.clicked.connect(
                partial(self.assign_speakers, item_0))
            self.speaker_legend.setItemWidget(item_0, 0, assign_button)

            self.row_to_speaker_object[self.speaker_legend.indexOfTopLevelItem(
                item_0)] = item_0
            self.speaker_to_row[name] = self.speaker_legend.indexOfTopLevelItem(
                item_0)
            speaker_names[name].append(self.icons[index])
            speaker_names[name].append(self.colors[index])

    def restore_table(self, speaker_names, conversation_data):
        """Build the table
        
        Args:
            speaker_names: Contain the information associated to each speaker.
                Such as audio file, log file, icon
            conversation_data (List): List containing the conversation data
        
        """
        self.api_timer.start(100)
        self.sud_timer.start(10000)
        self.progress.show()
        self.conversation_table.setAutoSwitchPage(False)
        rowC = len(conversation_data)
        for index, data in enumerate(conversation_data):
            speaker_icon = QtWidgets.QTableWidgetItem()
            speaker_icon.setTextAlignment(QtCore.Qt.AlignCenter)
            font = QtGui.QFont()
            font.setPointSize(15)
            speaker_icon.setFont(font)
            speaker_icon.setIcon(speaker_names[data[0]][7])
            speaker_icon.setData(QtCore.Qt.UserRole,
                                 speaker_names[data[0]][5] + ':' + data[0])
            speaker_icon.setBackground(QBrush(QColor(
                speaker_names[data[0]][8][0], speaker_names[data[0]][8][1], speaker_names[data[0]][8][2], speaker_names[data[0]][8][3])))
            
            speaker_start = QtWidgets.QTableWidgetItem()
            speaker_start.setText(data[1])
            font = QtGui.QFont()
            font.setPointSize(15)
            speaker_start.setFont(font)
            speaker_start.setBackground(QBrush(QColor(
                speaker_names[data[0]][8][0], speaker_names[data[0]][8][1], speaker_names[data[0]][8][2], speaker_names[data[0]][8][3])))

            speaker_end = QtWidgets.QTableWidgetItem()
            speaker_end.setText(data[2])
            font = QtGui.QFont()
            font.setPointSize(15)
            speaker_end.setFont(font)
            speaker_end.setBackground(QBrush(QColor(
                speaker_names[data[0]][8][0], speaker_names[data[0]][8][1], speaker_names[data[0]][8][2], speaker_names[data[0]][8][3])))

            speaker_message = QtWidgets.QTableWidgetItem()
            speaker_message.setText(data[3].replace('\\n', '\n' ))
            speaker_message.setData(
                QtCore.Qt.UserRole, self.speaker_to_row[data[0]])#select_module_handler
            # self.tablemodel.insertRow(index,speaker_icon,speaker_start,speaker_end,speaker_message,file)
            self.conversation_table.insertRow(index)
            self.conversation_table.setItem(index, 0, speaker_icon)
            self.conversation_table.setItem(index, 1, speaker_start)
            self.conversation_table.setItem(index, 2, speaker_end)
            self.conversation_table.setItem(index, 3, speaker_message)
            self.conversation_table.setItem(index, 4, file)
            # if self.model =="eng_closetalk" or  self.model =="eng_telephony" or self.model =="engmalay_closetalk"  or self.model =="cs_closetalk" :
            #         sudurl= self.config['SUD']['english_url']
            # else:
            #      sudurl= self.config['SUD']['english_url']
            # sud_data = {"input_text": data[3]}
            # header_data = {
            #     "API_KEY": self.config['SUD']['api_key'],
            #     "API_SECRET": self.config['SUD']['api_secret']
            # }
            
            # self.sud_requests.put((self.req_session.post( sudurl,
            #   data=sud_data, timeout=4, hooks={'response': self.parentresp(index, None, sud_data, header_data),
            # }), index, None, sud_data, header_data))
            
            
            # self.api_request.put([self.req_api_session.get(self.config['API']['server'] + "apiServer/" +data[3], hooks={'response': self.parentresp1(index)}),index,data[3]])
            self.progress.setValue(index/rowC*100)
        self.conversation_table.setAutoSwitchPage(True)
        self.conversation_table.switchPage(1)
            

    def record_button_handler(self):
        self.window.statusbar.showMessage('Recording Started', 2000)

        currindex = 0
        for mic_id in self.mic_ids:
            thread_dict = {}
            for channel in self.mic_ids[mic_id]:
                self.model = model_selector(self.mic_ids[mic_id][channel][0], self.config)
                print("Selected Model:" + str(self.model))
                uri = self.config['ASR']['gateway']
                endpoint_sampling_rate = 8000 if int( self.mic_ids[mic_id][channel][0].split('_')[1]) == 8000 else 16000
                content_type = 'audio/x-raw, layout=(string)interleaved, rate=(int)' + str(
                    endpoint_sampling_rate) + ', format=(string)S16LE, channels=(int)1'
                #get AccessToken
                access_token = self.window.access_token
                # Old service.ini
                #access_token = self.config['ASR']['access_token']
                if self.is_filemode:
                    thread_dict[channel] = MyClient(uri + '?%s' % (urllib.parse.urlencode([("content-type", content_type)])) + '&%s' % (urllib.parse.urlencode([("accessToken", access_token)])) + '&%s' % (urllib.parse.urlencode([("model", self.model)])), channel,
                                                    mic_id=mic_id, icon=self.mic_ids[mic_id][channel][4], customsignal=self.customsignal, color=self.colors[currindex], endpoint_sampling_rate=endpoint_sampling_rate, meetingname=self.meetingname, speaker_name=self.mic_ids[mic_id][channel][1], filename=self.mic_ids[mic_id][channel][3], byterate=2*self.mic_ids[mic_id][channel][2], window=self.window,model=self.model)
                    self.playback[str(mic_id) + '-' + str(channel)] = self.mic_ids[mic_id][channel][3]
                else:
                    thread_dict[channel] = MyClient(uri + '?%s' % (urllib.parse.urlencode([("content-type", content_type)])) + '&%s' % (urllib.parse.urlencode([("accessToken", access_token)])) + '&%s' % (urllib.parse.urlencode([("model", self.model)])), channel,
                                                    mic_id=mic_id, icon=self.mic_ids[mic_id][channel][3], customsignal=self.customsignal, color=self.colors[currindex], endpoint_sampling_rate=endpoint_sampling_rate, meetingname=self.meetingname, speaker_name=self.mic_ids[mic_id][channel][1], byterate=2*self.mic_ids[mic_id][channel][2], window=self.window,model=self.model)

                self.mic_threads[str(mic_id) + '-' +
                                 str(channel)] = thread_dict[channel]
                self.mic_ids[mic_id][channel][-1].setEnabled(True)
                self.mic_ids[mic_id][channel][-2].setEnabled(True)
                currindex = currindex + 1
            mode = 'file' if self.is_filemode else 'stream'
            r_thread = RecordThread(
                len(self.mic_ids[mic_id]), self.mic_ids[mic_id][1][2], mic_id, thread_dict, mode, self.config['ASR']['silence_timeout'])
            self.record_threads[mic_id] = r_thread

        if 'SUD' in self.config.sections() and self.config['SUD']['enable_sud'] == 'Y':
            self.sud_timer.start(10000)

        self.meeting_status.setText('Ongoing')
        self.record_button.hide()
        self.prevscreen_button.hide()
        self.stop_button.show()
        self.pause_button.show()
        # self.test.start()
        # self.summary_button.show() # uncomment when summary feature is stable

    def start_recording(self, mic_id):
        if not self.record_threads[mic_id].isRunning():
            self.record_threads[mic_id].start()
            if not self.is_filemode and not self.is_restoremode:
                self.record_time_remaining_timer.start()

    def stop_button_handler(self):
        if self.session_stopped:	
            return
        print('Stopping Recording')
        self.window.statusbar.showMessage('Stopping Recording', 2000)
        if not self.is_filemode and not self.is_restoremode:
            self.record_time_remaining_timer.stop()

        for r_thread in self.record_threads:
            self.record_threads[r_thread].isStop = True
            self.record_threads[r_thread].wait(2000)
            

        filenamepart = []
        for mic_thread in self.mic_threads:

            counter = 1
            mic = int(mic_thread.split('-')[0])
            channel = int(mic_thread.split('-')[1])
            
            if not self.is_filemode:
                self.mic_threads[mic_thread].wave_file.close()

                final_wav = wave.open('./' + slugify(
                    self.meetingname+'-'+self.mic_ids[mic][channel][1])+ '-part-'+str(counter)+'.wav', 'wb')
                final_wav.setsampwidth(2)
                final_wav.setframerate(
                    self.mic_threads[mic_thread].endpoint_sampling_rate)
                final_wav.setnchannels(1)
                frameRate = final_wav.getframerate();
                SpiltFileSec = 3600
                
                for i in range(1, self.mic_threads[mic_thread].currentpart + 1):
                    partfile = wave.open('./' + slugify(
                        self.meetingname+'-'+self.mic_ids[mic][channel][1]) + '-' + str(i) + '.wav', 'rb')
                    final_wav.writeframes(
                        partfile.readframes(partfile.getnframes()))
                    partfile.close()
                    os.remove('./' + slugify(
                        self.meetingname+'-'+self.mic_ids[mic][channel][1]) + '-' + str(i) + '.wav')
                    
                    numOfFrame = final_wav.getnframes()
                    if(numOfFrame/frameRate > SpiltFileSec):
                        final_wav.close()
                        filenamepart.append(('./' + slugify(self.meetingname+'-'+self.mic_ids[mic][channel][1])+ '-part-'+str(counter)+'.wav'))
                        counter = counter + 1
                        final_wav = wave.open('./' + slugify(
                            self.meetingname+'-'+self.mic_ids[mic][channel][1]) + '-part-'+str(counter)+'.wav', 'wb')
                        final_wav.setsampwidth(2)
                        final_wav.setframerate(
                            self.mic_threads[mic_thread].endpoint_sampling_rate)
                        final_wav.setnchannels(1)
                        
                filenamepart.append(('./' + slugify(self.meetingname+'-'+self.mic_ids[mic][channel][1])+ '-part-'+str(counter)+'.wav'))
                final_wav.close()

            self.mic_ids[mic][channel][-1].setEnabled(False)
            self.mic_ids[mic][channel][-2].setEnabled(False)

            if self.is_filemode:
                self.playback[mic_thread] = self.mic_ids[mic][channel][3]
            else:
                self.playback[mic_thread] = filenamepart

        self.session_stopped = True
        print('Recording Stopped')
        self.window.statusbar.showMessage('Recording Stopped', 5000)
        self.meeting_status.setText('Finished')
        self.stop_button.hide()
        self.pause_button.hide()
        self.log_button.show()
        self.playaudio_button.show()
        self.stopaudio_button.show()
        self.gv.show()
        

    def log_directory(self):
        log_directory = QtWidgets.QFileDialog.getExistingDirectory(self,"Select a folder to save logs?",".",QtWidgets.QFileDialog.ShowDirsOnly)
        return log_directory
    
    def log_directory_saveType(self,default_FileName):
        log_directory = QtWidgets.QFileDialog.getSaveFileName(self,"Save File",default_FileName,filter=self.tr(".stm",".Textgrid"))
        return log_directory
    
    
    def build_xml_sentence(self,orignalSentence,SpeechSegment,speaker_message,speaker_name,start_time,end_time):
        #check if any changes is made
        sentence = []
        for Word in orignalSentence:
            sentence.append(Word.text+" ")
        orignalmessage = ''.join(sentence)
        if orignalmessage.strip() == speaker_message.strip():
            SpeechSegment.set("stime",orignalSentence.attrib["stime"])
            SpeechSegment.set("dur", orignalSentence.attrib["dur"])
            SpeechSegment.set("spkrid",speaker_name)
            for Words in orignalSentence:
                Word = SubElement(SpeechSegment, "Word")
                Word.text = Words.text
                Word.set("stime",Words.attrib["stime"])
                Word.set("dur",Words.attrib["dur"])
                Word.set("score",Words.attrib["score"])
        else:
            #sentence
            SpeechSegment.set("stime",start_time)
            SpeechSegment.set("dur",str(format(float(end_time)-float(start_time), '.2f')))
            SpeechSegment.set("spkrid",speaker_name)
            Word = SubElement(SpeechSegment, "Word")
            Word.text = speaker_message
            Word.set("stime",start_time)
            Word.set("dur",str(format(float(end_time)-float(start_time), '.2f')))
            Word.set("score","1")
        return SpeechSegment
    
    def save(self):
        self.savetype = 'overwrite'
        self.dialog.accept()
    def saveas(self):
        self.savetype = 'revision'
        self.dialog.accept()
    def reject(self):
        self.savetype = "cancel"    
        self.dialog.accept()
        
        
    def log_button_handler(self, boolcheck, event=None):
        if 'SUD' in self.config.sections() and self.config['SUD']['enable_sud'] == 'Y':
            self.sud_timer.stop()
            self.window.statusbar.showMessage('Processing Sud Requests', 2000)

        savetype = ''
        saveMethod = ''
        
        
        self.dialog = Dialog()   
        self.dialog.setWindowFlag(QtCore.Qt.WindowCloseButtonHint, False)
        self.dialog.box.accepted.connect(self.save)
        self.dialog.box.helpRequested.connect(self.reject)
        self.dialog.box.rejected.connect(self.saveas)
        self.dialog.exec_()
        self.dialog.deleteLater()
 
        if self.savetype == 'cancel':
            return
        if self.savetype == 'revision' :
            self.log_path = self.log_directory()
            if self.log_path == '':
                self.window.statusbar.showMessage(
                    'Please select a folder to save logs.', 2000)
                return

        self.window.statusbar.showMessage('Saving Logs', 2000)

        chat_log = {}
        log_text = ''
        singlegrid = [[], None, None, '.TextGrid', -1, -1]
        srtindex = 1
        root_list = {}
        root= ''
        
        # if saveMethod != 'splitBySpeaker':
        #     saveByFile = True # Saving by File
        # else:
        #     saveByFile = False
        saveByFile=True
        
        #( )

        # Saving Data
        file_format=self.dialog.combo.currentText()
        buttonID = self.dialog.radioGroup.checkedId()
        if buttonID == 0:
            self.saveWithHtml = True
        else:
            self.saveWithHtml = False
        for i in range(self.conversation_table.rowCount()):
            dev_id, speaker_name = self.conversation_table.item(i, 0).data(QtCore.Qt.UserRole).split(':')
            #Key use to decide saving by speaker or file
            if(self.is_restoremode):
                original = self.conversation_table.item(i, 4).data(QtCore.Qt.UserRole)

            speaker_name_file = speaker_name

            if self.is_restoremode:
                start_time = self.conversation_table.item(i, 1).text().strip()
                end_time = self.conversation_table.item(i, 2).text().strip()
                speaker_message = self.conversation_table.item(i, 3).text().strip().replace('\n', '\\n').replace('\r', ' ').strip()
                if not self.saveWithHtml:
                    speaker_message = cleanhtml(speaker_message)
                speaker_name = self.row_to_speaker_object[self.conversation_table.item(i, 3).data(QtCore.Qt.UserRole)].text(1)
                meeting_name = self.mic_ids[speaker_name_file][6]
                #file_format = '.' + self.mic_ids[speaker_name_file][4].split('.')[-1]
                if(saveByFile):
                    speaker_name_file = original
                else:
                    speaker_name_file = meeting_name + '__' + speaker_name
                    original = speaker_name
            else:
                try:
                    start_time, end_time = self.conversation_table.item(i, 3).text().strip().split(':')
                    end_time = str("{:.2f}".format(float(end_time)))
                    speaker_message = self.conversation_table.item(i, 2).text().strip().replace('\n', ' ').replace('\r', ' ').strip()
                    if not self.saveWithHtml:
                        speaker_message = cleanhtml(speaker_message)
                except:
                    print("Error in saving skip" + str(i))
                    continue
                speaker_name = speaker_name_file
                meeting_name = self.meetingname
                #file_format = '.stm'
                speaker_name_file = slugify(meeting_name + '-' + speaker_name)
                if(saveByFile):
                    original = speaker_name

            if self.is_restoremode and self.num_mics == 1:
                if file_format == '.srt':
                    log_text = log_text + str(i+1) + '\n' + timedelta_to_srt_timestamp(datetime.timedelta(
                        seconds=float(start_time))) + ' --> ' + timedelta_to_srt_timestamp(datetime.timedelta(seconds=float(end_time))) + '\n' + speaker_message + '\n\n'
                elif file_format == '.TextGrid':
                    if i != 0:
                        preItemIndex = len(singlegrid[0]) - 1
                        preItemStartTime = singlegrid[0][preItemIndex][0]
                        preItemEndTime = singlegrid[0][preItemIndex][1]
                        
                        if start_time>preItemEndTime:
                            singlegrid[0].append((preItemEndTime, start_time, "--EMPTY--", speaker_name))

                    singlegrid[4] = start_time
                    singlegrid[5] = end_time
                    singlegrid[0].append((start_time, end_time, speaker_message, speaker_name))
                elif file_format == '.xml':   
                    if(i == 0):
                        if(self.xmlRoot.get(original) is None):
                            root = Element("AudioDoc")
                            root.set("name",chat_log[original][1].split(".")[0].split("/")[-1])
                        else:
                            root = Element(self.xmlRoot[original].tag)
                            root.set("name",self.xmlRoot[original].attrib["name"])
                        segmentlist = SubElement(root, 'SegmentList')

                    if(self.xmlRoot.get(original) is None):
                        orignalSentence =""
                    else:     
                        orignalSentence = self.xmlRoot[original][0][i]
                    
                    SpeechSegment = SubElement(segmentlist, 'SpeechSegment')
                    SpeechSegment.set("channel","1")
                    SpeechSegment.set("score","1")
                    SpeechSegment.set("lang","eng")
                    SpeechSegment.set("gender","1")
                    SpeechSegment.set("band","s")
                    SpeechSegment = self.build_xml_sentence(orignalSentence,SpeechSegment,speaker_message,speaker_name,start_time,end_time)
                else:
                    log_text = log_text + meeting_name + ' ' + dev_id + ' ' + speaker_name + ' ' + start_time + ' ' + end_time + ' ' + '<0,f0,male>' + ' ' + speaker_message + '\n'
                
            else:
                if chat_log.get(original, None) is None:
                    if file_format == '.TextGrid' or file_format == '.xml' :
                        chat_log[original] = [[], speaker_name_file, dev_id, file_format, start_time, end_time]
                    else:
                        chat_log[original] = ['', speaker_name_file, dev_id, file_format, start_time, end_time]

                if float(end_time) > float(chat_log[original][5]):
                    chat_log[original][5] = end_time
                if file_format == '.srt':
                    chat_log[original][0] = chat_log[original][0] + str(srtindex) + '\n' + timedelta_to_srt_timestamp(datetime.timedelta(
                        seconds=float(start_time))) + ' --> ' + timedelta_to_srt_timestamp(datetime.timedelta(seconds=float(end_time))) + '\n' + speaker_message + '\n\n'
                    srtindex = srtindex + 1
                elif file_format == '.TextGrid' or file_format == '.xml' :
                    if file_format == '.TextGrid':
                        preItemIndex = len(chat_log[original][0]) - 1
                        if preItemIndex >-1:
                            preItemStartTime = chat_log[original][0][preItemIndex][0]
                            preItemEndTime = chat_log[original][0][preItemIndex][1]
                            
                            if start_time>preItemEndTime:
                                chat_log[original][0].append((preItemEndTime, start_time, "--EMPTY--", speaker_name))
                    
                    chat_log[original][0].append((start_time, end_time, speaker_message, speaker_name))
                else:
                    if self.reconnect_messages.get(i, None) is not None:
                        speaker_message = '** ' + speaker_message
                    chat_log[original][0] = chat_log[original][0] + meeting_name + ' ' + dev_id + ' ' + slugify(speaker_name) + ' ' + start_time + ' ' + end_time + ' ' + '<0,f0,male>' + ' ' + speaker_message + '\n'
        
        if self.is_restoremode and self.num_mics == 1:
            filesaving_path = self.mic_ids[[*self.mic_ids][0]][4]
            file_name = filesaving_path.split('.')[0]
            filesaving_path = file_name +file_format
            if self.savetype != 'overwrite':
                filesaving_path = self.log_path + '/' + filesaving_path.split('/')[-1]
            
            with open(filesaving_path, 'w+', encoding="utf-8") as logfile:
                if file_format == '.TextGrid':
                    textgrid_string = write_to_textgrid(singlegrid, meeting_name)
                    logfile.write(textgrid_string)
                if(file_format =='.xml' ):
                    log = ET.tostring(root, encoding='utf8', method='xml')
                    reparsed = minidom.parseString(log)
                    logfile.write(str(reparsed.toprettyxml(indent="  ")))
                logfile.write(log_text)
        else:
            for speaker in chat_log:
                # if self.savetype != 'overwrite':
                filesaving_path = self.log_path +"/" +chat_log[speaker][1].split(".")[0].split("/")[-1] + chat_log[speaker][3]
                # else:
                    # filesaving_path = speaker
                if not os.path.exists(self.log_path):
                    os.makedirs(self.log_path)
                    print(self.log_path)
                with open(filesaving_path, 'w+',encoding="utf-8") as logfile:
                    if chat_log[speaker][3] == '.TextGrid':
                        textgrid_string = write_to_textgrid(chat_log[speaker], speaker)
                        logfile.write(textgrid_string)
                    elif chat_log[speaker][3] == '.xml':
                        if(self.xmlRoot.get(speaker) is None):
                            root = Element("AudioDoc")
                            root.set("name",chat_log[speaker][1].split(".")[0].split("/")[-1])
                        else:
                            root = Element(self.xmlRoot[speaker].tag)
                            root.set("name",self.xmlRoot[speaker].attrib["name"])
                        
                        segmentlist = SubElement(root, 'SegmentList')
                        messageList = chat_log[speaker][0]
                        count = 0
                        for message in messageList:
                            start_time  = message[0]
                            end_time  = message[1]
                            speaker_message = message[2]
                            speaker_name = message[3]
                            if(self.xmlRoot.get(speaker) is None):	
                                orignalSentence =""	
                            else:
                                orignalSentence = self.xmlRoot[speaker][0][count]
                            SpeechSegment = SubElement(segmentlist, 'SpeechSegment')
                            SpeechSegment.set("channel","1")
                            SpeechSegment.set("score","1")
                            SpeechSegment.set("lang","eng")
                            SpeechSegment.set("gender","1")
                            SpeechSegment.set("band","s")
                            SpeechSegment = self.build_xml_sentence(orignalSentence,SpeechSegment,speaker_message,speaker_name,start_time,end_time)
                            count = count + 1
                            
                        log = ET.tostring(root, encoding='utf8', method='xml')
                        reparsed = minidom.parseString(log)
                        logfile.write(str(reparsed.toprettyxml(indent="  ")))
                    else:
                        logfile.write(chat_log[speaker][0])
                        
                # move file only for "new" button
                if not self.is_restoremode :
                    if not self.is_filemode:
                        counter = 1 ;
                        filenamepart = []
                        for old_path in glob.glob('./' + chat_log[speaker][1] + '*.wav'):
                            new_path = self.log_path + '/' + chat_log[speaker][1] + '-part-'+ str(counter)+'.wav'
                            filenamepart.append(new_path)
                            if not os.path.exists(self.log_path):
                                os.makedirs(self.log_path)
                            shutil.move(old_path, new_path)
                            counter += 1
                        self.playback[chat_log[speaker][2]] = filenamepart

        self.log_saved = True
        self.window.statusbar.showMessage('Logs saved', 2000)
        if event is not None:
            event.accept()

    def pause_button_handler(self):
        self.session_isPaused = not self.session_isPaused

        if self.session_isPaused:
            if not self.is_filemode and not self.is_restoremode:
                self.record_time_remaining_timer.stop()
            for mic_thread in self.mic_threads:
                # self.mic_threads[mic_thread].pause = timer()
                if self.mic_threads[mic_thread].client.state() != QAbstractSocket.UnconnectedState and self.mic_threads[mic_thread].is_disconnected == False:
                    self.mic_threads[mic_thread].send_signal.emit('EOS', 'text', 'paused')
                    # self.mic_threads[mic_thread].is_paused = True
                    mic = int(mic_thread.split('-')[0])
                    channel = int(mic_thread.split('-')[1])
                    self.mic_ids[mic][channel][-1].setEnabled(False)
                    self.mic_ids[mic][channel][-2].setEnabled(False)

            self.window.statusbar.showMessage('Recording Paused', 2000)
            self.meeting_status.setText('On a break')
            self.pause_button.setText('Resume')

            return

        for mic_thread in self.mic_threads:
            if not self.is_filemode and not self.is_restoremode:
                self.record_time_remaining_timer.start()
            current_thread = self.mic_threads[mic_thread]
            if not current_thread.is_disconnected:
                current_thread.reconnect()
                mic = int(mic_thread.split('-')[0])
                channel = int(mic_thread.split('-')[1])
                self.mic_ids[mic][channel][-1].setEnabled(True)
                self.mic_ids[mic][channel][-2].setEnabled(True)

        self.window.statusbar.showMessage('Recording Resumed', 2000)
        self.meeting_status.setText('Ongoing')
        self.pause_button.setText('Pause')

    def setup_speaker_legend(self):
        currindex = 0
        for mic_id in self.mic_ids:
            for channel in self.mic_ids[mic_id]:
                item_0 = QtWidgets.QTreeWidgetItem(self.speaker_legend)
                item_0.setText(1, self.mic_ids[mic_id][channel][1])
                font = QtGui.QFont()
                font.setPointSize(15)
                item_0.setFont(1, font)
                item_0.setIcon(1, self.icons[currindex])
                item_0.setBackground(1, QBrush(QColor(
                    255, 0, 0, 100)))

                reconnect_button = QtWidgets.QPushButton()
                reconnect_button.setObjectName("reconnect_button")
                reconnect_button.setGeometry(QtCore.QRect(500, 30, 211, 131))
                reconnect_button.setIcon(self.reconnect_icon)
                reconnect_button.setEnabled(False)

                disconnect_button = QtWidgets.QPushButton()
                disconnect_button.setObjectName("disconnect_button")
                disconnect_button.setGeometry(QtCore.QRect(500, 30, 211, 131))
                disconnect_button.setIcon(self.disconnect_icon)
                disconnect_button.setEnabled(False)

                two_buttons = QtWidgets.QWidget()
                two_button_layout = QtWidgets.QHBoxLayout()
                two_button_layout.setSpacing(0)
                two_button_layout.setContentsMargins(0, 0, 0, 0)
                two_button_layout.addWidget(
                    disconnect_button, 0, QtCore.Qt.AlignLeft)
                two_button_layout.addWidget(
                    reconnect_button, 0, QtCore.Qt.AlignRight)
                two_buttons.setLayout(two_button_layout)

                self.speaker_legend.setItemWidget(item_0, 0, two_buttons)

                reconnect_button.clicked.connect(
                    partial(self.reconnect_button_handler, str(mic_id)+'-'+str(channel), 'MANUAL'))
                disconnect_button.clicked.connect(
                    partial(self.disconnect_button_handler, str(mic_id)+'-'+str(channel)))

                self.mic_ids[mic_id][channel].append(self.icons[currindex])
                self.mic_ids[mic_id][channel].append(item_0)
                self.mic_ids[mic_id][channel].append(disconnect_button)
                self.mic_ids[mic_id][channel].append(reconnect_button)
                self.color_mic_mapping[str(
                    mic_id) + '-' + str(channel)] = self.colors[currindex]

                currindex = currindex + 1

    def reconnect_button_handler(self, mic_id, reconnect_type):
        current_thread = self.mic_threads[mic_id]
        if reconnect_type == 'MANUAL':
            current_thread.send_signal.emit('EOS', 'text', 'reconnect')
            if current_thread.client.state() == QAbstractSocket.UnconnectedState:
                current_thread.reconnect()

            if self.mic_status.get(mic_id, None) is not None:
                self.reconnect_messages[self.mic_status.get(mic_id)] = 1
            else:
                self.reconnect_messages[self.conversation_table.rowCount(
                )] = 1

    def update_treeitem_background(self, tree_item, color, mic_id, channel_id):
        if tree_item:
            tree_item.setBackground(
                1, QBrush(QColor(color[0], color[1], color[2], color[3])))

            return

        treeitem = self.mic_ids[mic_id][channel_id][-3]
        treeitem.setBackground(
            1, QBrush(QColor(color[0], color[1], color[2], color[3])))

    def disconnect_button_handler(self, mic_id):
        current_thread = self.mic_threads[mic_id]
        current_thread.send_signal.emit('EOS', 'text', 'stopped')
        current_thread.is_disconnected = True
        mic = int(mic_id.split('-')[0])
        channel = int(mic_id.split('-')[1])
        treeitem = self.mic_ids[mic][channel][-3]
        treeitem.setBackground(1, QBrush(QColor(255, 0, 0, 100)))
        self.mic_ids[mic][channel][-1].setEnabled(False)
        self.mic_ids[mic][channel][-2].setEnabled(False)
        

    def setup_icons(self):
        icon_list = []

        for i in range(1, 11):
            icon = QtGui.QIcon()
            icon.addPixmap(QtGui.QPixmap(resource_path('./icons/' + str(i) + '.png')),
                           QtGui.QIcon.Normal, QtGui.QIcon.Off)
            icon_list.append(icon)

        return icon_list

    def add_message(self, post_text, mic_id, channel_id, icon, color, start_time, end_time,model):
        
        # self.api_request.put([self.req_api_session.get(self.config['API']['server'] + "apiServer/" +post_text,hooks={'response': self.parentresp1(self.api_counter)}),self.api_counter,post_text])
        self.api_timer.start(10000)
        self.api_counter = self.api_counter + 1
        
        speaker_item = QtWidgets.QTableWidgetItem()
        speaker_item.setTextAlignment(QtCore.Qt.AlignCenter)
        font = QtGui.QFont()
        font.setPointSize(15)
        speaker_item.setFont(font)
        speaker_item.setIcon(icon)
        speaker_item.setData(QtCore.Qt.UserRole, mic_id + '-' + str(channel_id) +':' + self.mic_ids[int(mic_id)][channel_id][1])
        speaker_item.setBackground(QBrush(QColor(color[0], color[1], color[2], color[3])))

        speaker_message = QtWidgets.QTableWidgetItem()
        speaker_message.setText(post_text)
        speaker_message.setData(QtCore.Qt.UserRole, self.mic_ids[int(mic_id)][channel_id][1])
        font = QtGui.QFont()
        font.setPointSize(15)
        speaker_message.setFont(font)
        speaker_message.setBackground(QBrush(QColor(color[0], color[1], color[2], color[3])))

        speaker_times = QtWidgets.QTableWidgetItem()

        speaker_times.setText(str(start_time) + ':' + str(end_time))
        font = QtGui.QFont()
        font.setPointSize(15)
        speaker_times.setFont(font)
        speaker_times.setBackground(QBrush(QColor(color[0], color[1], color[2], color[3])))

        max_slider_pos = self.conversation_table.verticalScrollBar().maximum()
        move_slider_to_bottom = False

        if self.conversation_table.verticalScrollBar().sliderPosition() >= max_slider_pos - 2:
            move_slider_to_bottom = True

        if self.mic_status.get(str(mic_id) + '-' + str(channel_id), None) is None:
            speaker_time = QtWidgets.QTableWidgetItem()
            current_time = datetime.datetime.now().strftime("%H:%M:%S")
            speaker_time.setText(current_time)
            font = QtGui.QFont()
            font.setPointSize(15)
            speaker_time.setFont(font)
            speaker_time.setBackground(
                QBrush(QColor(color[0], color[1], color[2], color[3])))

            self.mic_status[str(mic_id) + '-' + str(channel_id)] = self.conversation_table.rowCount()
            self.conversation_table.insertRow(self.mic_status[str(mic_id) + '-' + str(channel_id)])
            self.conversation_table.setItem(self.mic_status[str(mic_id) + '-' + str(channel_id)], 1, speaker_time)

        if move_slider_to_bottom:
            self.conversation_table.scrollToBottom()

        self.conversation_table.setItem(
            self.mic_status[str(mic_id) + '-' + str(channel_id)], 0, speaker_item)
        self.conversation_table.setItem(
            self.mic_status[str(mic_id) + '-' + str(channel_id)], 2, speaker_message)
        self.conversation_table.setItem(
            self.mic_status[str(mic_id) + '-' + str(channel_id)], 3, speaker_times)

    
        if 'SUD' in self.config.sections() and self.config['SUD']['enable_sud'] == 'Y':
            sud_data = {"input_text": post_text}
            print('posting text: ', end=" ")
            print(post_text)
            header_data = {
                "API_KEY": self.config['SUD']['api_key'],
                "API_SECRET": self.config['SUD']['api_secret']
            }
            if model =="eng_closetalk" or  model =="eng_telephony" or model =="engmalay_closetalk"  or model =="cs_closetalk" :
                    sudurl= self.config['SUD']['english_url']
            else:
                 sudurl= self.config['SUD']['chinese_url']
            self.sud_requests.put((self.req_session.post(sudurl,
                                                        data=sud_data, timeout=4, hooks={
                                                             'response': self.parentresp(self.mic_status[str(mic_id) + '-' + str(channel_id)], color, sud_data, header_data),
            }), self.mic_status[str(mic_id) + '-' + str(channel_id)], color, sud_data, header_data))

        del self.mic_status[str(mic_id) + '-' + str(channel_id)]



    
    def buildColorTable(self):
        for i in range(len(self.config["COLORCODE"])):
            item1 = QtWidgets.QTableWidgetItem()
            item2 = QtWidgets.QTableWidgetItem()
            self.ColorCodeTable.insertRow(i)
            self.ColorCodeTable.setItem(i, 0, item1)
            self.ColorCodeTable.setItem(i, 1, item2)
        
        count = 0 
        for item in self.config["COLORCODE"]:
            self.ColorCodeTable.item(count,1).setBackground(QColor(webcolors.name_to_hex(self.config["COLORCODE"][item])))
            self.ColorCodeTable.item(count,0).setText(item)
            count = count + 1
        
        # self.ColorCodeTable.item(0,1).setBackground(QColor('#112233'))
        # self.ColorCodeTable.item(1,1).setBackground(QtCore.Qt.green)
        # self.ColorCodeTable.item(2,1).setBackground(QtCore.Qt.blue)
        # self.ColorCodeTable.item(3,1).setBackground(QtCore.Qt.yellow)
        # self.ColorCodeTable.item(4,1).setBackground(QtCore.Qt.cyan)
        # self.ColorCodeTable.item(5,1).setBackground(QtCore.Qt.magenta)
        
        # self.ColorCodeTable.item(0,0).setText("PERSON")
        # self.ColorCodeTable.item(1,0).setText("GPE")
        # self.ColorCodeTable.item(2,0).setText("ORG")
        # self.ColorCodeTable.item(3,0).setText("DATE")
        # self.ColorCodeTable.item(4,0).setText("CARDINAL")
        # self.ColorCodeTable.item(5,0).setText("Others")
        
    def parentresp1(self, index, *parentargs, **parentkwargs):
        def response_hook1(resp, *args, **kwargs):
            # parse the json storing the result on the response object
            data = resp.content.decode("utf-8")
            receivedJson = json.loads(data)
            receivedJson = json.loads(receivedJson)
            resp.data = receivedJson
            string_list = []
            for word in receivedJson["main"]:
                string = word["entity"][0]+" " +word["entity"][1]
                string_list.append(string)
            self.api_data[index] = string_list
            
            if (self.is_restoremode):
                textItem = self.conversation_table.item(index,3)
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
                    text = insert_str(textIndex,text,"<"+en_type+">")
                    
                    textIndex = text.find(entity)
                    text = insert_str(textIndex+len(entity),text,"<"+en_type+">")

                    textItem.setText(text)
                self.conversation_table.setItem(index, 3, textItem)
            else:
                textItem = self.conversation_table.item(index,2)
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
                    text = insert_str(textIndex,text,"<"+en_type+">")
                    
                    textIndex = text.find(entity)
                    text = insert_str(textIndex+len(entity),text,"</"+en_type+">")
                    
                    textItem.setText(text)
                self.conversation_table.setItem(index, 2, textItem)
            
            
            print(receivedJson)
            return resp
        # self.conversation_table.viewport().repaint()
        return response_hook1

    def parentresp(self, rownum, color, sud_data, header_data, *parentargs, **parentkwargs):
        def response_hook(resp, *args, **kwargs):
            print(resp.json()['result'],rownum)
            punctuated_textitem = QtWidgets.QTableWidgetItem(resp.json()['result'])
            font = QtGui.QFont()
            font.setPointSize(15)
            punctuated_textitem.setFont(font)
            punctuated_textitem.setBackground(
                QBrush(QColor(color[0], color[1], color[2], color[3])))

            if (self.is_restoremode):
                self.conversation_table.setItem(rownum, 3, punctuated_textitem)
            else:
                self.conversation_table.setItem(rownum, 2, punctuated_textitem)
                
                
            self.api_request.put([self.req_api_session.get(self.config['API']['server'] + "apiServer/" +resp.json()['result'],hooks={'response': self.parentresp1(rownum)}),rownum,resp.json()['result']])
            
            
            self.summary_messages = self.summary_messages + \
                resp.json()['result']
            resp.data = resp.json()['result']
            
            return resp
        return response_hook

    def update_message(self, post_text, mic_id, channel_id, icon, color):
        speaker_item = QtWidgets.QTableWidgetItem()
        speaker_item.setTextAlignment(QtCore.Qt.AlignCenter)
        font = QtGui.QFont()
        font.setPointSize(15)
        speaker_item.setFont(font)
        speaker_item.setIcon(icon)
        speaker_item.setData(QtCore.Qt.UserRole, mic_id + '-' + str(channel_id) +
                             ':' + self.mic_ids[int(mic_id)][channel_id][1])
        speaker_item.setBackground(
            QBrush(QColor(color[0], color[1], color[2], color[3])))

        speaker_message = QtWidgets.QTableWidgetItem()
        speaker_message.setText(post_text)
        font = QtGui.QFont()
        font.setPointSize(15)
        speaker_message.setFont(font)
        speaker_message.setForeground(QBrush(QColor(255, 0, 0)))
        speaker_message.setBackground(
            QBrush(QColor(color[0], color[1], color[2], color[3])))

        max_slider_pos = self.conversation_table.verticalScrollBar().maximum()
        move_slider_to_bottom = False

        if self.conversation_table.verticalScrollBar().sliderPosition() >= max_slider_pos - 2:
            move_slider_to_bottom = True

        if self.mic_status.get(str(mic_id) + '-' + str(channel_id), None) is None:
            speaker_time = QtWidgets.QTableWidgetItem()
            current_time = datetime.datetime.now().strftime("%H:%M:%S")
            speaker_time.setText(current_time)
            font = QtGui.QFont()
            font.setPointSize(15)
            speaker_time.setFont(font)
            speaker_time.setBackground(
                QBrush(QColor(color[0], color[1], color[2], color[3])))

            self.mic_status[str(mic_id) + '-' + str(channel_id)
                            ] = self.conversation_table.rowCount()
            self.conversation_table.insertRow(
                self.mic_status[str(mic_id) + '-' + str(channel_id)])
            self.conversation_table.setItem(
                self.mic_status[str(mic_id) + '-' + str(channel_id)], 1, speaker_time)

        if move_slider_to_bottom:
            self.conversation_table.scrollToBottom()

        self.conversation_table.setItem(
            self.mic_status[str(mic_id) + '-' + str(channel_id)], 0, speaker_item)
        self.conversation_table.setItem(
            self.mic_status[str(mic_id) + '-' + str(channel_id)], 2, speaker_message)


    def thread_function(self):
        request_queue_size = self.api_request.qsize()
        for i in range(request_queue_size):
            req_data = self.api_request.get()
            try:
                response = req_data[0].result()
            except Exception as e:
                #print('error: ' + str(e))
                if(self.failed>20):
                    break
                index = req_data[1]
                text = req_data[2]
                retry = 0
                #print("length : " + str(len(req_data)))
                if len(req_data) == 4:
                    retry = req_data[3]
                    retry = retry + 1
                if(retry < 2):
                    print("Error : Retrying API Request," + "Tries : " + str(retry) +" Text :" + text)
                    self.api_request.put([self.req_api_session.get(self.config['API']['server'] + "apiServer/" +text, hooks={'response': self.parentresp1(index)}),index,text,retry])             
                    self.failed = self.failed + 1
        
    def api_response_handler(self):
        if self.failed <21:
            self.x = threading.Thread(target=self.thread_function)
            self.x.start()
        else:
            self.api_timer.stop()
            
    def sud_thread(self):	
        self.y = threading.Thread(target=self.sud_response_handler)	
        self.y.start()
        
    def sud_response_handler(self):
        request_queue_size = self.sud_requests.qsize()

        for i in range(request_queue_size):
            req_data = self.sud_requests.get()
            try:
                response = req_data[0].result()
            except Exception as e:
                print('error: ' + str(e))
                self.conversation_table.item(req_data[1], 0).setBackground(
                    QBrush(QColor(255, 0, 0, 100)))
                self.conversation_table.item(req_data[1], 1).setBackground(
                    QBrush(QColor(255, 0, 0, 100)))
                self.conversation_table.item(req_data[1], 2).setBackground(
                    QBrush(QColor(255, 0, 0, 100)))
                # send request again
                print('posting text after error: ', end=" ")
                self.sud_requests.put((self.req_session.post(
                    self.config['SUD']['english_url'], data=req_data[3], timeout=4, hooks={
                        'response': self.parentresp(req_data[1], req_data[2], req_data[3], req_data[4]),
                    }), req_data[1], req_data[2], req_data[3], req_data[4]))

    def update_summary(self, summary):
        self.summary_box.setText(summary)
        self.summary_button.setEnabled(True)

    def summary_button_handler(self):
        if not self.summary_isVisible:
            self.summary_box.setHtml(self.summary_text)
            self.summary_box.show()
            self.summary_isVisible = True
            self.summary_button.setEnabled(False)

            s_thread = SummaryThread(
                self.req_session, self.summary_messages, self.customsignal)
            s_thread.start()
            self.sthreads.append(s_thread)

            return

        self.summary_box.hide()
        self.summary_text = 'Fetching Summary!!!'
        self.summary_isVisible = False

    def increase_playrate(self):
        self.current_play_rate = self.current_play_rate + 0.2
        self.current_play_rate = float(
            '{0:.1f}'.format(self.current_play_rate))
        self.vlc_mediaplayer.set_rate(self.current_play_rate)
        self.currentrate_button.setText(str(self.current_play_rate))
        rem_time = self.duration - \
            (self.vlc_mediaplayer.get_time() - self.slider_start)
        if rem_time != -1:
            time = rem_time / self.current_play_rate
            self.player_timer.stop()
            self.player_timer.start(time)

    def decrease_playrate(self):
        old_rate = self.current_play_rate
        self.current_play_rate = self.current_play_rate - 0.2
        self.current_play_rate = float(
            '{0:.1f}'.format(self.current_play_rate))
        self.vlc_mediaplayer.set_rate(self.current_play_rate)
        self.currentrate_button.setText(str(self.current_play_rate))
        rem_time = self.duration - \
            (self.vlc_mediaplayer.get_time() - self.slider_start)
        if rem_time != -1:
            time = rem_time * old_rate
            self.player_timer.stop()
            self.player_timer.start(time)

    def reset_currentrate(self):
        if self.current_play_rate != 1.0:
            old_rate = self.current_play_rate
            self.current_play_rate = 1.0
            self.vlc_mediaplayer.set_rate(self.current_play_rate)
            self.currentrate_button.setText(str(self.current_play_rate))
            rem_time = self.player_timer.remainingTime()
            if rem_time != -1:
                time = rem_time * old_rate
                self.player_timer.stop()
                self.player_timer.start(time)
                return
            self.remaining_time = self.remaining_time * old_rate

    def update_speakers(self, old_speaker, new_speaker, tree_row):
        if old_speaker != 'Please enter a speaker name':
            del self.speaker_to_row[old_speaker]
        if self.row_to_speaker_object.get(tree_row, None) is None:
            item = CustomTreeWidgetItem(
                self.speaker_legend, customsignal=self.customsignal)
            item.setText(1, new_speaker)
            item.setFlags(item.flags() | QtCore.Qt.ItemIsEditable)
            font = QtGui.QFont()
            font.setPointSize(15)
            item.setFont(1, font)
            item.setIcon(
                1, self.icons[tree_row])
            color = self.colors[tree_row]
            item.setBackground(
                1, QBrush(QColor(color[0], color[1], color[2], color[3])))
            assign_button = QtWidgets.QPushButton()
            assign_button.setObjectName("assign_button")
            assign_button.setGeometry(QtCore.QRect(500, 30, 211, 131))
            assign_button.setIcon(self.assign_icon)
            assign_button.clicked.connect(partial(self.assign_speakers, item))
            self.speaker_legend.setItemWidget(item, 0, assign_button)
            self.row_to_speaker_object[tree_row] = item
        self.row_to_speaker_object[tree_row].setText(1, new_speaker)
        self.speaker_to_row[new_speaker] = tree_row

    def managespeakers(self):
        a = Ui_manage_speakers_top_layout(
            self.speaker_legend, self.conversation_table, self.customsignal, self.icons, self.colors)

        if a.exec():
            print('dialog accept')
        else:
            print('dialog close')

    def delete_speakers(self, row_num, speaker_name):
        num_rows = len(self.row_to_speaker_object)
        self.speaker_legend.takeTopLevelItem(row_num)
        del self.row_to_speaker_object[row_num]
        del self.speaker_to_row[speaker_name]
        for index in range(row_num, num_rows - 1):
            self.row_to_speaker_object[index] = self.row_to_speaker_object[index+1]

    def assign_speakers(self, speaker_name):
        if type(speaker_name) == CustomTreeWidgetItem:
            speaker_name = speaker_name.text(1)
        selected_messages = self.conversation_table.selectedItems()
        new_row = self.speaker_to_row[speaker_name]
        speaker_object = self.row_to_speaker_object[new_row]
        for item in range(3, len(selected_messages), 4):
            selected_messages[item-3].setBackground(speaker_object.background(1))
            selected_messages[item-3].setIcon(speaker_object.icon(1))
            selected_messages[item-2].setBackground(speaker_object.background(1))
            selected_messages[item-1].setBackground(speaker_object.background(1))
            selected_messages[item].setBackground(speaker_object.background(1))
            
            #dev_id, old = selected_messages[0].data(QtCore.Qt.UserRole).split(':')
            #new = dev_id +":"+speaker_name
            #selected_messages[0].setData(QtCore.Qt.UserRole,new)
            selected_messages[item].setData(QtCore.Qt.UserRole, new_row)

    def enable_change_speakers(self):
        #print(self.conversation_table.item(0, 3).text())
        #print(self.conversation_table.item(0, 0).data(QtCore.Qt.UserRole))
        # self.testing.clear()
        # row = self.conversation_table.selectionModel().selectedRows()
        row = self.conversation_table.currentRow()
        # try:
        #     api_data = self.api_data[row]
        #     for d in api_data:
        #         QtWidgets.QTreeWidgetItem(self.testing, [d])
        # except:
        #     print()
        # BASE = self.config['API']['server']
        # response = requests.get(BASE + "apiServer/" +self.conversation_table.item(row, 3).text())
        # receivedJson = response.json()
        # receivedJson = json.loads(receivedJson) 
        # for word in receivedJson["main"]:
        #     string = word["entity"][0]+" " +word["entity"][1]
        #     QtWidgets.QTreeWidgetItem(self.testing, [string])
            
            
        # doc = self.nlp(self.conversation_table.item(row, 3).text())
        # for ent in doc.ents:
            
        #     string = ent.text +" " +ent.label_
            
        #     QtWidgets.QTreeWidgetItem(self.testing, [string])
            
        if self.is_restoremode:
            start_time = self.conversation_table.item(
                row, 1).text().strip()
            end_time = self.conversation_table.item(row, 2).text().strip()
        else:
            try:
                start_time, end_time = self.conversation_table.item(
                    row, 3).text().strip().split(':')
            except:
                start_time = None
                end_time = None

        if start_time is not None and end_time is not None:
            start_time = (float(start_time)) * 1000  # milliseconds
            end_time = (float(end_time)) * 1000  # milliseconds
            self.duration = end_time - start_time
            self.set_pos_rem_time = -1
            if self.vlc_mediaplayer.get_state() != vlc.State.Playing:
                self.slider_start = start_time
                self.remaining_time = self.duration / self.current_play_rate
                label_range = range(0, int((end_time-start_time)/1000)+1, 1)
                self.positionslider.levels = list(
                    zip(label_range, map(str, label_range)))
                self.positionslider.sl.setMaximum(int((end_time-start_time)/1000))
                self.positionslider.update()
                
                micid, speakername = self.conversation_table.item(row, 0).data(QtCore.Qt.UserRole).split(':')
                micid_speaker = micid if (self.session_stopped or self.is_filemode) else speakername
                print("micid_speaker" + str(micid_speaker))
                clip, self.offset =  self.clipToPlay(start_time/1000, micid_speaker)
                duration = (end_time - start_time)/1000
                if clip == None:
                    x = []
                else:
                    x, sr = librosa.load(clip, sr =self.samplerate, offset = (start_time/1000) - self.offset, duration= duration)
                print(self.offset)
                print((start_time/1000) - self.offset)
                
                self.removeGraphItem("waveform")
                self.removeGraphItem("InfiniteLine")

                self.p1 = pg.PlotDataItem(name = "waveform")
                ar = np.arange(0, len(x))
                ar = ar + (start_time/1000)*self.samplerate
                self.p1.setData(y=x, x=ar)
                self.p2 = pg.InfiniteLine(ar[0])
                self.vb.addItem(self.p1)
                self.vb.addItem(self.p2)
                self.vb.setRange(rect=None, xRange=[ar[0],ar[0]+(self.samplerate*duration)], yRange=None, padding=0, update=True, disableAutoRange=True)
                self.xScale.setScale(1/self.samplerate)

            self.curr_position_slider = start_time
        if row != self.play_row and self.vlc_mediaplayer.get_state() != vlc.State.Playing:
            self.positionslider.sl.setValue(0)
        if self.is_restoremode:
            self.managespeakers_button.show()

        if len(self.conversation_table.selectionModel().selectedRows()) > 1:
            self.playaudio_button.hide()
            self.stopaudio_button.hide()
            self.increaserate_button.hide()
            self.currentrate_button.hide()
            self.decreaserate_button.hide()
            self.positionslider.hide()
            return

        if self.session_stopped or self.is_restoremode or self.is_filemode:
            self.playaudio_button.show()
            self.stopaudio_button.show()
            self.increaserate_button.show()
            self.currentrate_button.show()
            self.decreaserate_button.show()
            self.positionslider.show()

    def removeGraphItem(self, item ):
        if item =="waveform":
            for i in range(len(self.vb.allChildren())):
                if isinstance(self.vb.allChildren()[i], pg.PlotDataItem):
                    self.vb.removeItem(self.vb.allChildren()[i])
                    return
        if item =="InfiniteLine":
            for i in range(len(self.vb.allChildren())):
                if isinstance(self.vb.allChildren()[i], pg.InfiniteLine):
                    self.vb.removeItem(self.vb.allChildren()[i])
                    return

    def update_slider_ui(self):
        if self.vlc_mediaplayer.is_playing():
            media_pos = int((self.vlc_mediaplayer.get_time() - self.slider_start + (self.offset*1000))/1000)
            self.positionslider.sl.setValue(media_pos)
        if self.vlc_mediaplayer.get_state() == vlc.State.Paused:
            media_pos = int((self.vlc_mediaplayer.get_time() - self.slider_start + (self.offset*1000))/1000)
            self.positionslider.sl.setValue(media_pos)

    def set_position(self, event):
        self.slider_timer.stop()
        self.player_timer.stop()
        self.positionslider.sl.setValue(QtWidgets.QStyle.sliderValueFromPosition(self.positionslider.sl.minimum(
        ), self.positionslider.sl.maximum(), event.x(), self.positionslider.sl.width()))
        pos = self.positionslider.sl.value() * 1000
        self.vlc_mediaplayer.set_time(int(pos + self.slider_start - self.offset*1000))
        self.curr_position_slider = pos + self.slider_start
        self.remaining_time = self.duration - pos
        if self.vlc_mediaplayer.get_state() == vlc.State.Playing:
            self.player_timer.start(self.remaining_time)
            self.slider_timer.start()
            return
        self.set_pos_rem_time = self.remaining_time

    def delete_transcript(self):
        rows = self.conversation_table.selectionModel().selectedRows()

        for row in rows:
            self.conversation_table.removeRow(row.row())

    def update_remaining_record_time(self):
        hours_available, minutes_available = self.get_recording_time_remaining()
        self.remaining_record_time.setText("Remaining Record Time: " + str(hours_available) + " hours " + str(minutes_available) + " min")

    def get_recording_time_remaining(self):
        current_free_space = shutil.disk_usage('.')
        current_free_space = current_free_space.free
        hours_available, minutes_available = divmod(int(current_free_space / self.ONE_MINUTE_RECORD_SIZE), 60)
        return hours_available, minutes_available
    
    def updateHotKey(self,funct,hotkey):
        self.hotkeyDict[funct].setKey(hotkey)

    
    # paging
    def focusTextBox(self):
        self.txtPage.setFocus(QtCore.Qt.ShortcutFocusReason)
    def nextButton(self):
        self.conversation_table.nextPage()
    def prevButton(self):
        self.conversation_table.prevPage()
        
    def skipFirst_handler(self):
        self.conversation_table.switchPage(1)

    def skipLast_handler(self):
        self.conversation_table.switchPage(len(self.conversation_table.pageLimitList))    
    
    def ListItemClicked(self):
        pageSelected = self.PageNumberList.selectedItems()[0].data(QtCore.Qt.UserRole)
        self.conversation_table.switchPage(pageSelected)
           # self.conversation_table.redrawList(pageSelected)
    
    def changeEntry(self):
        self.conversation_table.changePageLimit(int(self.comboBox.currentText()))

    def PageJump(self):
        if(self.txtPage.text().strip() == ""): return
        self.conversation_table.switchPage(int(self.txtPage.text()))

    def eventFilter(self, source, event):
        if(event.type() == QtCore.QEvent.MouseButtonPress and
           event.buttons() == QtCore.Qt.RightButton and
           source is self.conversation_table.viewport()):
            item = self.conversation_table.itemAt(event.pos())
            #print('Global Pos:', event.globalPos())
            if item is not None:
                #print('Table Item:', item.row(), item.column())
                self.menu = QtWidgets.QMenu(self)
                self.action = QtWidgets.QAction("Bookmark")
                self.action.triggered.connect(self.bookMark)
                self.menu.addAction(self.action)        
                self.action2 = QtWidgets.QAction("Split Page")
                self.action2.triggered.connect(self.splitPage)
                self.menu.addAction(self.action2)        
                #menu.exec_(event.globalPos())
        return super(Ui_fourth_screen, self).eventFilter(source, event)

    def bookMark(self):
        self.conversation_table.createBookMark()
        
    def splitPage(self):
        index = self.conversation_table.currentRow()
        self.conversation_table.splitPage(index)
        
    def generateMenu(self, pos):
        print("pos======",pos)
        self.menu.exec_(self.conversation_table.mapToGlobal(pos))   #

    def conversation_table_custom_handler(self, rows_required):
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


        FullData = self.conversation_table.FullData
        pageData = self.conversation_table.pageData
        pageLimit = self.conversation_table.pageLimit
        pageLimitList = self.conversation_table.pageLimitList
        page = self.conversation_table.page
        self.conversation_table_dialog = ConversationTableDialog(rows_required, FullData, pageData, pageLimit, pageLimitList, page, self.customsignal)
        #self.conversation_table_dialog.conversation_table.FullData = self.conversation_table.FullData
        self.conversation_table_dialog.setWindowFlag(QtCore.Qt.WindowCloseButtonHint, False)
        self.conversation_table_dialog.showMaximized()
        #self.module_select_dialog.box.accepted.connect(self.module_select_accept)
        #self.module_select_dialog.box.rejected.connect(self.module_select_reject)
        
        if self.conversation_table_dialog.exec_():
            print("Exec Conv Table Dialog")
        else:
            print("")
        
        self.conversation_table_dialog.deleteLater()
        sip.delete(self.conversation_table_dialog)
        #self.conversation_table_dialog.clear()

    def select_module_handler(self):
        selected_modules = []
        #modules_info = ['NER', 'Event', 'Sound']
        module_select_dialog = ModuleSeletorDialog(self.modules)
        module_select_dialog.setWindowFlag(QtCore.Qt.WindowCloseButtonHint, False)

        
        if module_select_dialog.exec_():
            for checkbox in module_select_dialog.checkboxes:
                if checkbox.isChecked():
                    selected_modules.append(checkbox.text())
                    print(checkbox.text())
        #self.module_select_dialog.deleteLater()
        rows_required = []
        for module in selected_modules:
            for row in self.module_row_numbers[module]:
                if(row not in rows_required):
                    rows_required.append(row)
        self.conversation_table_custom_handler(rows_required)

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

        ner_table_dialog = NER_TableDialog(pageData)
        if ner_table_dialog.exec_():
            print("NER Table EXEC")
        else:
            print("")

class CustomTableWidget1(QtWidgets.QTableWidget):
    """A custom table class which inherit from QTableWidget that supports pagination
    """
    def __init__(self, rows_required):
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
        self.rows_required = rows_required

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
        #self.redrawList(self.page)
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
        global shared_FullData
        for key in shared_FullData:
            self.FullData[key] = shared_FullData[key]
        if(pageID > len(self.pageLimitList)): return
        # self.pageData = self.getPageSlice()
        self.duplicate()
        self.page = pageID
        self.pageData = self.getPageSlice()
        self.setRowCount(0)
        print("Page : " + str(self.page))
        self.buildPage()
        self.FullData.clear()
        #self.redrawList(pageID)

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
        #self.redrawList(1)
        # self.bookmarksList = []
            
    def duplicate(self):
        """Duplicate the data in self.FullData 
        
        Whenever current page data change, self.setRowCount(0) is called to clear table content. 
        Therefore, items in self.FullData will be removed from the memory. Hence, we will create a new instance of
        QTableWidgetItem and copy the important feature needed such as text, data, color...etc.
        To improve performace, a dirty bit (self.FullData[key][1]) is set to prevent duplicating the whole full data.      
        
        """
        # Set current page dirty bit
        # lp, up = self.getLimits2(self.page)
        # for i in range(up-lp):
        #     if (lp+i+1) in self.FullData:
        #         self.FullData[lp+i+1][1] = True
        #     else:
        #         break
        # for key in self.FullData:
        #     if(self.FullData[key][1]):
        #         rowData = self.FullData[key]
        #         self.FullData[key][0] = rowData[0]
        #         self.FullData[key][1] = False
        #         colIndex = 2
        #         for data in rowData:
        #             if isinstance(data,QtWidgets.QTableWidgetItem):
        #                 dup = QtWidgets.QTableWidgetItem()
        #                 dup.setText(data.text())
        #                 dup.setData(QtCore.Qt.UserRole,data.data(QtCore.Qt.UserRole))
        #                 dup.setBackground(data.background())
        #                 dup.setFont(data.font())
        #                 dup.setIcon(data.icon())
        #                 self.FullData[key][colIndex] = dup
        #                 colIndex = colIndex + 1
        temp = {}
        for key in shared_FullData:
            temp[key] = shared_FullData[key]
        lp, up = self.getLimits2(self.page)
        for i in range(up-lp):
            if (lp+i+1) in temp:
                temp[lp+i+1][1] = True
            else:
                break
        for key in shared_FullData:
            if(temp[key][1]):
                rowData = temp[key]
                temp[key][0] = rowData[0]
                temp[key][1] = False
                colIndex = 2
                for data in rowData:
                    if isinstance(data,QtWidgets.QTableWidgetItem):
                        dup = QtWidgets.QTableWidgetItem()
                        dup.setText(data.text())
                        dup.setData(QtCore.Qt.UserRole,data.data(QtCore.Qt.UserRole))
                        dup.setBackground(data.background())
                        dup.setFont(data.font())
                        dup.setIcon(data.icon())
                        temp[key][colIndex] = dup
                        colIndex = colIndex + 1
        self.FullData = temp
            
                      
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
        #self.redrawList(self.page)
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
        #self.redrawList(self.page)

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
            print(i+lowerlimit+1)
            #print(self.rows_required)
            if i+lowerlimit+1 in self.FullData:
                if i+lowerlimit+1 in self.rows_required:
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
            item1.setSizeHint(QSize(self.listitemsize,1))
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
        #if self.bool:
        #    self.redrawList(self.page)
            
    def resizeEvent(self, event):
        """Called whenever the window size change. QListWidget will be re-drawn to fit the size
        """
        #if self.bool:
        #    self.redrawList(self.page)
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

    def custom_switchPage(self,pageID):
        """Switch the table to a specific page number
        
        Args:
            pageID (int): Page number

        """
        if(pageID > len(self.pageLimitList)): return
        # self.pageData = self.getPageSlice()
        self.pageData = self.custom_getPageSlice()
        self.setRowCount(0)
        print("Page : " + str(self.page))
        self.custom_buildPage()
        #self.redrawList(pageID)

    def custom_getPageSlice(self):
        """Get the current page data information from self.fullData
        
        Returns:
            listData(List): Return current page data as a list
     
        """
        lowerlimit,upperlimit = self.getLimits()
        listData = []
        for i in range((upperlimit+1)-(lowerlimit+1)):
            if i+lowerlimit+1 in self.FullData and i+lowerlimit+1 in self.rows_required:
                listData.append(self.FullData[i+lowerlimit+1])
            else: 
                break
        return listData

    def custom_buildPage(self):
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





