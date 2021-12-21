import urllib
import configparser
import os
import time
import tempfile
import wave
import socket
from PyQt5.QtCore import QThread
from PyQt5.QtCore import pyqtSignal as Signal
from utilities.asr import MyClient
from slugify import slugify


class MicThread(QThread):

    def __init__(self, mic_id, chatui, language_choice, sampling_rate, icon, color, custsignal, channel, totalchannels, filename=None):
        QThread.__init__(self)

        self.config = configparser.ConfigParser()
        self.config.read('services.ini')

        self.mic_id = mic_id
        self.language_choice = language_choice
        self.sampling_rate = sampling_rate
        self.icon = icon
        self.chatui = chatui
        self.color = color
        self.customsignal = custsignal
        self.channel = channel
        self.totalchannels = totalchannels
        self.filename = filename
        self.is_disconnected = False
        self.is_paused = True
        self.reconnect_counter = 0
        self.last_message = 0
        self.offset = 0
        self.customsignal.reconnect_counter.connect(
            self.reconnect_counter_update)
        self.mode = 'file' if self.filename else 'stream'
        self.uri = self.uri_selector()
        self.endpoint_sampling_rate = 8000 if int(
            self.language_choice.split('_')[1]) == 8000 else 16000
        print(self.endpoint_sampling_rate)
        self.content_type = 'audio/x-raw, layout=(string)interleaved, rate=(int)' + str(
            self.endpoint_sampling_rate) + ', format=(string)S16LE, channels=(int)1'
        self.access_token = self.config['ASR']['access_token']
        self.wave_file = wave.open(tempfile.gettempdir() + '/' + slugify(
            self.chatui.meetingname+'-'+self.chatui.mic_ids[self.mic_id][self.channel][1]) + '.wav', 'wb')  # opening the file
        self.wave_file.setsampwidth(2)
        self.wave_file.setframerate(self.endpoint_sampling_rate)
        self.wave_file.setnchannels(1)
        self.ws = MyClient(self.mode, self.filename, self.uri + '?%s' % (urllib.parse.urlencode([("content-type", self.content_type)])) + '?%s' % (urllib.parse.urlencode([("token", self.access_token)])), self.wave_file, self.channel, byterate=2*self.sampling_rate,
                           mic_id=self.mic_id, rate=self.sampling_rate, icon=self.icon, customsignal=self.customsignal, meeting_name=self.chatui.meetingname, speaker_name=self.chatui.mic_ids[self.mic_id][1], color=self.color, thread_obj=self)

    def __del__(self):
        self.wave_file.close()

    def run(self):
        try:
            self.ws.connect()
            s = time.time()
            result = self.ws.get_full_hyp()
            e = time.time()
            print('total time: ' + str(e-s))
            print(result)
        except socket.timeout:
            print('Connecting to websocket timedout. Please check ASR server is running or the address to ASR server is correct.')

    def uri_selector(self):
        if self.language_choice == 'english_16000':
            uri = self.config['ASR']['ip_english_16k']
        elif self.language_choice == 'mandarin_16000':
            uri = self.config['ASR']['ip_mandarin_16k']
        elif self.language_choice == 'english-mandarin_16000':
            uri = self.config['ASR']['ip_eng_mandarin_16k']
        elif self.language_choice == 'english-malay_16000':
            uri = self.config['ASR']['ip_eng_malay_16k']
        if self.language_choice == 'english_8000':
            uri = self.config['ASR']['ip_english_8k']
        elif self.language_choice == 'mandarin_8000':
            uri = self.config['ASR']['ip_mandarin_8k']
        elif self.language_choice == 'english-mandarin_8000':
            uri = self.config['ASR']['ip_eng_mandarin_8k']
        elif self.language_choice == 'english-malay_8000':
            uri = self.config['ASR']['ip_eng_malay_8k']

        return uri

    def reconnect_counter_update(self):
        self.reconnect_counter = self.reconnect_counter + 1
