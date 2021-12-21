from PyQt5 import QtCore, QtGui, QtWidgets
from .thirdscreen import Ui_third_screen
from functools import partial
from utilities.utils import getDeviceIndices, getDeviceInfo, getSupportedRate
import numpy as np
import PySimpleGUI as sg
import pyaudio
import wave
from array import array
from struct import pack
import threading


class Ui_second_screen(QtWidgets.QWidget):
    """Asr_GUI Ui_second_screen window class
    
    Attributes:
        num_mics (int): Number of microphone
        devices_info (List): The local computer microphone device information
        prev_screen (QWidget): Hold the previous widget/Screen. This is used to go back to previous screen
       
    
    """
    def __init__(self, window, num_mics, prev_screen=None):
        """Inits Ui_second_screen
        
        Args:
            num_mics (int): The number of devices user entered
            prev_screen (QWidget): Previous screen


        """
        QtWidgets.QWidget.__init__(self)

        self.num_mics = num_mics
        self.window = window
        self.devices_info = getDeviceInfo()
        self.prev_screen = prev_screen

    def setupUi(self):
        """Setup the UI
        
        This method need to be called after the class has been instantiated. This method will create the GUI for
        our window.
    
            
        """
        self.setObjectName("second_screen")
        screen_width = (self.window.available_width -
                        60) if self.window.available_width < 700 else 700
        screen_height = (self.window.available_height -
                         60) if self.window.available_height < 700 else 700
        self.setMaximumHeight(screen_height)
        self.resize(screen_width, screen_height)

        self.verticalLayout = QtWidgets.QVBoxLayout(self)
        self.verticalLayout.setObjectName("verticalLayout")

        self.screen_label = QtWidgets.QLabel(self)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.screen_label.sizePolicy().hasHeightForWidth())
        self.screen_label.setSizePolicy(sizePolicy)
        self.screen_label.setAlignment(QtCore.Qt.AlignCenter)
        self.screen_label.setObjectName("screen_label")
        self.verticalLayout.addWidget(self.screen_label)

        self.parent_alldevice_hbox = QtWidgets.QHBoxLayout()
        self.parent_alldevice_hbox.setObjectName('parentlayout')
        self.parent_alldevice_hbox.insertSpacing(0, 40)

        self.alldevice_layout = QtWidgets.QVBoxLayout()
        self.alldevice_layout.insertSpacing(0, 10)
        self.alldevice_layout.setSpacing(6)
        self.alldevice_layout.setObjectName("alldevice_layout")

        self.checkboxes = []
        self.volume_buttons = []
        self.record_audio_buttons = []
        self.add_checkboxes()

        self.parent_alldevice_hbox.addLayout(self.alldevice_layout)
        self.verticalLayout.addLayout(self.parent_alldevice_hbox)

        self.alldevice_layout.addStretch()

        self.button_layout = QtWidgets.QHBoxLayout()
        self.button_layout.setAlignment(QtCore.Qt.AlignCenter)
        self.button_layout.setObjectName("button_layout")

        self.prevscreen_button = QtWidgets.QPushButton(self)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.prevscreen_button.sizePolicy().hasHeightForWidth())
        self.prevscreen_button.setSizePolicy(sizePolicy)
        self.prevscreen_button.setObjectName("prevscreen_button")
        self.button_layout.addWidget(self.prevscreen_button)

        self.next_button = QtWidgets.QPushButton(self)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.next_button.sizePolicy().hasHeightForWidth())
        self.next_button.setSizePolicy(sizePolicy)
        self.next_button.setObjectName("next_button")
        self.button_layout.addWidget(self.next_button)

        self.verticalLayout.addLayout(self.button_layout)
        self.verticalLayout.setStretch(1, 1)

        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)

        self.deviceone_multicheckbox.hide()
        self.deviceone_multiselect.hide()

        self.next_button.clicked.connect(self.next_button_handler)
        self.prevscreen_button.clicked.connect(self.prevscreen_handler)
        self.deviceone_checkbox.stateChanged.connect(partial(
            self.state_changed, self.deviceone_checkbox, self.deviceone_multicheckbox, self.deviceone_multiselect))
        self.deviceone_multicheckbox.stateChanged.connect(partial(
            self.state_changedmulti, self.deviceone_checkbox, self.deviceone_multicheckbox, self.deviceone_multiselect))
        self.device_indices = getDeviceIndices()
        #print(self.device_indices)

        # for button in self.volume_buttons:
        #     print(self.device_indices[self.volume_buttons.index(button)])

        for self.button in self.volume_buttons:
            self.button.clicked.connect(self.volume_test_handler, self.device_indices[self.volume_buttons.index(self.button)])

        for button in self.record_audio_buttons:
            button.clicked.connect(self.record_audio_handler, self.device_indices[self.record_audio_buttons.index(button)])


    def record_audio_handler(self, dev_index):
        def record():
            CHUNK = 1024
            FORMAT = pyaudio.paInt16
            CHANNELS = 2
            RATE = 44100
            RECORD_SECONDS = 5

            p = pyaudio.PyAudio()
            stream = p.open(format=FORMAT, channels=CHANNELS,rate = RATE,input = True, input_device_index=dev_index, frames_per_buffer=CHUNK)
            print("--recording--")
            frames = []
            for i in range(0, int(RATE/CHUNK*RECORD_SECONDS)):
                data = stream.read(CHUNK)
                frames.append(data)
            
            print("--recording complete--")

            stream.stop_stream()
            stream.close()
            p.terminate()

            wf = wave.open("testFile.wav", 'wb')
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(p.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(frames))
            wf.close()

        def play(file):
            CHUNK = 1024
            wf = wave.open(file, 'rb')
            p=pyaudio.PyAudio()
            stream = p.open(format = p.get_format_from_width(wf.getsampwidth()),
                                                            channels=wf.getnchannels(),
                                                            rate = wf.getframerate(),
                                                            output=True)
            data = wf.readframes(CHUNK)
            while len(data) > 0 :
                stream.write(data)
                data = wf.readframes(CHUNK)
            stream.stop_stream()
            stream.close()
            p.terminate()

        record()
        play('testFile.wav')



    def volume_test_handler_thread(self, dev_index):
        thread = threading.Thread(target=self.volume_test_handler, args=(str(dev_index),), daemon=True)
        thread.start()
        #thread.join()
        
    def volume_test_handler(self, dev_index):
        dev_index = int(dev_index)
        _VARS = {'window': False,'stream': False}
        # pysimpleGUI INIT:
        AppFont = 'Any 16'
        sg.theme('DarkTeal2')
        layout = [[sg.ProgressBar(4000, orientation='h',
                                size=(20, 20), key='-PROG-')],
                [sg.Button('Listen', font=AppFont),
                sg.Button('Stop', font=AppFont, disabled=True)]]
                #sg.Button('Exit', font=AppFont)]]
        _VARS['window'] = sg.Window('Microphone Level', layout, finalize=True)


        # PyAudio INIT:
        CHUNK = 1024  # Samples: 1024,  512, 256, 128
        RATE = 44100  # Equivalent to Human Hearing at 40 kHz
        INTERVAL = 1  # Sampling Interval in Seconds ie Interval to listen

        pAud = pyaudio.PyAudio()

        def stop():
            if _VARS['stream']:
                _VARS['stream'].stop_stream()
                _VARS['stream'].close()
                _VARS['window']['-PROG-'].update(0)
                _VARS['window']['Stop'].Update(disabled=True)
                _VARS['window']['Listen'].Update(disabled=False)
        
        def callback(in_data, frame_count, time_info, status):
            # print(in_data)
            data = np.frombuffer(in_data, dtype=np.int16)
            # print(np.amax(data))
            _VARS['window']['-PROG-'].update(np.amax(data))
            return (in_data, pyaudio.paContinue)

        def listen():
            _VARS['window']['Stop'].Update(disabled=False)
            _VARS['window']['Listen'].Update(disabled=True)
            _VARS['stream'] = pAud.open(format=pyaudio.paInt16,
                                        channels=1,
                                        rate=RATE,
                                        input=True,
                                        input_device_index=dev_index,
                                        frames_per_buffer=CHUNK,
                                        stream_callback=callback)

            _VARS['stream'].start_stream()

                # MAIN LOOP
        while True:
            event, values = _VARS['window'].read()
            if event == sg.WIN_CLOSED or event == 'Exit':
                stop()     
                break
            if event == 'Listen':
                listen()
            if event == 'Stop':
                stop()
                break
        pAud.terminate()   
        _VARS['window'].close()

    

    def prevscreen_handler(self):
        """Go back to previous screen
        """
        self.window.centralwidget.setCurrentWidget(self.prev_screen)
        
    
    def add_checkboxes(self):
        """Add checkboxes and Text
        
        This method will add checkboxes and text based on the self.devices_info
        
        """
        data = self.devices_info

        for dev in data:
            self.device_layout1 = QtWidgets.QHBoxLayout()
            self.device_layout1.setObjectName("device_layout1")

            self.deviceone_checkbox = QtWidgets.QCheckBox(self)
            self.deviceone_checkbox.setText(dev)
            sizePolicy = QtWidgets.QSizePolicy(
                QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Maximum)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(
                self.deviceone_checkbox.sizePolicy().hasHeightForWidth())
            self.deviceone_checkbox.setSizePolicy(sizePolicy)
            self.deviceone_checkbox.setObjectName("deviceone_checkbox")

            self.record_audio_button = QtWidgets.QPushButton(self)
            sizePolicy = QtWidgets.QSizePolicy(
                QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(
                self.record_audio_button.sizePolicy().hasHeightForWidth())
            self.record_audio_button.setSizePolicy(sizePolicy)
            self.record_audio_button.setObjectName("record_audio_button")

            self.volume_check_button = QtWidgets.QPushButton(self)
            sizePolicy = QtWidgets.QSizePolicy(
                QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(
                self.volume_check_button.sizePolicy().hasHeightForWidth())
            self.volume_check_button.setSizePolicy(sizePolicy)
            self.volume_check_button.setObjectName("volume_check_button")
            

            self.device_layout1.addWidget(self.deviceone_checkbox,
            alignment=QtCore.Qt.AlignLeft)
            self.device_layout1.addWidget(self.record_audio_button, alignment=QtCore.Qt.AlignRight)
            self.device_layout1.addWidget(self.volume_check_button, alignment=QtCore.Qt.AlignRight)

            self.device_multichannel_layout1 = QtWidgets.QHBoxLayout()
            self.device_multichannel_layout1.setContentsMargins(
                20, -1, 400, -1)
            self.device_multichannel_layout1.setObjectName(
                "device_multichannel_layout1")
            self.deviceone_multicheckbox = QtWidgets.QCheckBox(self)
            self.deviceone_multicheckbox.setText("Use multi channels?")
            sizePolicy = QtWidgets.QSizePolicy(
                QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
            sizePolicy.setHorizontalStretch(1)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(
                self.deviceone_multicheckbox.sizePolicy().hasHeightForWidth())
            self.deviceone_multicheckbox.setSizePolicy(sizePolicy)
            self.deviceone_multicheckbox.setObjectName(
                "deviceone_multicheckbox")

            self.device_multichannel_layout1.addWidget(
                self.deviceone_multicheckbox)

            self.deviceone_multiselect = QtWidgets.QComboBox(self)
            self.deviceone_multiselect.setObjectName("deviceone_multiselect")
            num_supported_channels = int(dev.split(': ')[-1])
            for i in range(2, num_supported_channels+1):
                self.deviceone_multiselect.addItem(str(i))

            self.device_multichannel_layout1.addWidget(
                self.deviceone_multiselect)

            self.device_layout1.addLayout(self.device_multichannel_layout1)
            self.alldevice_layout.addLayout(self.device_layout1)

            self.deviceone_multicheckbox.hide()
            self.deviceone_multiselect.hide()

            self.deviceone_checkbox.stateChanged.connect(partial(
                self.state_changed, self.deviceone_checkbox, self.deviceone_multicheckbox, self.deviceone_multiselect))
            self.deviceone_multicheckbox.stateChanged.connect(partial(
                self.state_changedmulti, self.deviceone_checkbox, self.deviceone_multicheckbox, self.deviceone_multiselect))
            self.checkboxes.append(
                [self.deviceone_checkbox, self.deviceone_multicheckbox, self.deviceone_multiselect])
            self.volume_buttons.append(self.volume_check_button)
            self.record_audio_buttons.append(self.record_audio_button)

    def retranslateUi(self):
        """Retranslate the UI
        """
        _translate = QtCore.QCoreApplication.translate
        self.window.setWindowTitle(_translate(
            "ASR - Select Mics", "ASR - Select Mics"))
        self.screen_label.setText(_translate(
            "second_screen", "Please select devices to use"))
        self.next_button.setText(_translate("second_screen", "Next"))
        self.prevscreen_button.setText(_translate("second_screen", "Back"))
        self.window.statusbar.showMessage(
            'Please select ' + str(self.num_mics) + ' devices.', 2000)
        for button in self.volume_buttons:
            button.setText(_translate(
            "second_screen", "Test Audio"))
        for button in self.record_audio_buttons:
            button.setText(_translate(
            "second_screen", "Record and Play"))

    def next_button_handler(self):
        """Next button event handler
        
        Instantiate Ui_third_screen
        
        """
        checked_boxes = []
        speaker_count = 0
        devices = {}
        for data in self.checkboxes:
            if data[0].isChecked():
                checked_boxes.append(data)

        # The selected checkbox must be = number of microphone 
        if len(checked_boxes) != self.num_mics:
            self.window.statusbar.showMessage(
                'please select only ' + str(self.num_mics) + ' mic', 2000)
            return

        for mic in checked_boxes:
            speaker_count = speaker_count + \
                int(mic[2].currentText()) if mic[1].isChecked(
                ) else speaker_count + 1
        if speaker_count > 8:
            self.window.statusbar.showMessage(
                "More than 8 speakers selected. A maximum of 8 speakers are allowed.", 3000)

            return
        for mic in checked_boxes:
            dev_id = int(mic[0].text().strip().split(
                'Input Device id ')[1].split(' -')[0])
            devices[dev_id] = {1: getSupportedRate(dev_id)}
            if mic[1].isChecked():
                for i in range(2, int(mic[2].currentText())+1):
                    devices[dev_id][i] = getSupportedRate(dev_id)
        self.third_screen = Ui_third_screen(self.window, devices, prev_screen=self)
        self.third_screen.setupUi()
        self.window.centralwidget.addWidget(self.third_screen)
        self.window.centralwidget.setCurrentWidget(self.third_screen)

    def state_changed(self, checktext, checkmultichannel, channelchoice, integer):
        if checktext.isChecked():
            checkmultichannel.show()
        else:
            checkmultichannel.setChecked(False)
            checkmultichannel.hide()
            channelchoice.hide()

    def state_changedmulti(self, checktext, checkmultichannel, channelchoice, integer):
        if checkmultichannel.isChecked():
            channelchoice.show()
        else:
            channelchoice.hide()
