import argparse
import time
import threading
import sys
import urllib
import queue
import json
import time
import os
import wave
import pyaudio
import numpy as np
import logging
        

from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5.QtCore import pyqtSignal as SIGNAL
from slugify import slugify
from PyQt5 import QtWebSockets
from PyQt5.QtCore import QObject, QUrl, pyqtSlot, QTimer
from PyQt5.QtNetwork import QAbstractSocket
from PyQt5.QtCore import pyqtSignal as Signal
from timeit import default_timer as timer
from PyQt5.QtWebSockets import QWebSocketProtocol
from datetime import datetime


FORMAT = pyaudio.paInt16
CHANNELS = 1


def rate_limited(maxPerSecond):
    minInterval = 1.0 / float(maxPerSecond)

    def decorate(func):
        lastTimeCalled = [0.0]

        def rate_limited_function(*args, **kargs):
            elapsed = time.clock() - lastTimeCalled[0]
            leftToWait = minInterval - elapsed
            if leftToWait > 0:
                time.sleep(leftToWait)
            ret = func(*args, **kargs)
            lastTimeCalled[0] = time.clock()
            return ret
        return rate_limited_function
    return decorate


class MyClient(QObject):
    send_signal = Signal(object, str, str)

    def __init__(self, url, channel, save_adaptation_state_filename=None, send_adaptation_state_filename=None, mic_id=1, icon=None, customsignal=None, color=None, endpoint_sampling_rate=None, meetingname=None, speaker_name=None, filename=None, byterate=None, window=None,model=None):
        super(MyClient, self).__init__()

        self.url = url
        # print(url)
        self.client = QtWebSockets.QWebSocket(
            "", QtWebSockets.QWebSocketProtocol.Version13, None)
        
        self.client.error.connect(self.error)
        self.client.open(QUrl(self.url))

        self.final_hyps = []
        self.final_hyp_queue = queue.Queue()
        self.save_adaptation_state_filename = save_adaptation_state_filename
        self.send_adaptation_state_filename = send_adaptation_state_filename
        self.mic_id = mic_id
        self.icon = icon
        self.customsignal = customsignal
        self.color = color
        self.channel = channel
        self.endpoint_sampling_rate = endpoint_sampling_rate
        self.last_message = 0
        self.offset = 0
        self.currentoffset = 0
        self.pause = 0
        self.countBlock = 0
        self.countBlockfix = 0
        self.start = None
        self.meetingname = meetingname
        self.speaker_name = speaker_name
        self.filename = filename
        self.byterate = byterate
        self.is_connected = False
        self.is_disconnected = True
        self.is_paused = True
        self.is_close = False
        self.window = window
        self.reconnect_counter = 0
        self.lastseg = 0
        self.model = model
        self.send_signal.connect(self.send_data)
        self.client.connected.connect(self.websocket_opened)
        self.client.textMessageReceived.connect(self.received_message)
        self.client.disconnected.connect(self.websocket_disconnected)
        self.client.pong.connect(self.onPong)
        self.client.sslErrors.connect(self.sslError)

        self.reconnectTimer = QTimer()
        self.reconnectTimer.timeout.connect(self.reconnect)


        self.setConnectTimer = QTimer()
        self.setConnectTimer.setSingleShot(True)
        self.setConnectTimer.timeout.connect(self.setConnect)


        # self.websocket_timer = QTimer()
        # self.websocket_timer.setSingleShot(True)
        # self.websocket_timer.timeout.connect(self.client.close)
        # self.websocket_timer.start(60000)

        self.currentpart = 1
        logging.getLogger("urllib3").setLevel(logging.WARNING)
        
        filepath = "Error" + str(self.mic_id) +".log"
        # self.logger = logging.getLogger()
        # if (self.logger.hasHandlers()):
        #     self.logger.handlers.clear()
        
        
        # fhandler = logging.FileHandler(filename=os.path.dirname(__file__)+filepath, mode='a')
        # fhandler.setFormatter(formatter)
        # self.logger.addHandler(fhandler)
        # self.logger.setLevel(logging.DEBUG)
        
        ## Error Summary for Debugging each speaker will have a log
        self.logger = self.setup_logger(filepath,os.path.dirname(__file__)+filepath)
        self.logger.info('Start session for :' + str(self.mic_id) +' channel ' + str(self.channel))
        self.errorDict = {}
        self.serverErrorDict = {}
        self.lastServerError = None
        self.lastError = None
        self.fastConnect=False


        if self.filename is None:
            self.wave_file = wave.open('./' + slugify(
                self.meetingname+'-'+self.speaker_name+'___' + str(self.currentpart)) + '.wav', 'wb')  # opening the file
            self.wave_file.setsampwidth(2)
            self.wave_file.setframerate(self.endpoint_sampling_rate)
            self.wave_file.setnchannels(1)
           
    def sslError(self,error):
        print(error.error())
        print(error.errorString())
    
    def setup_logger(self, name, log_file, level=logging.INFO):
        formatter = logging.Formatter(u'%(levelname)8s %(asctime)s %(message)s ')
        handler = logging.FileHandler(log_file)        
        handler.setFormatter(formatter)
        
        logger = logging.getLogger(name)
        if (logger.hasHandlers()):
            logger.handlers.clear()
        logger.setLevel(logging.DEBUG)
        logger.addHandler(handler)
        
        return logger

    def do_ping(self):
        print("client: do_ping")
        self.client.ping(b"keepalive")

    def onPong(self, elapsedTime, payload):
        print("onPong - time: {} ; payload: {}".format(elapsedTime, payload))


    @pyqtSlot(QAbstractSocket.SocketError)
    def error(self, error_code):
        print('Websocket error in mic ' + str(self.mic_id) +' channel ' + str(self.channel))
        print("Websocket error code: {}".format(error_code))
        print('Websocket error ', self.client.errorString())
        
        if error_code in self.errorDict:    
            arrayData = self.errorDict[error_code]
            arrayData[1] = arrayData[1] + 1
            arrayData[3] = timer() 
            self.errorDict[error_code] = arrayData
            
        else:
            self.errorDict[error_code] = [self.client.errorString(),1,0,timer()]
        self.errorDict[error_code].append(datetime.now())
        
        self.lastError = error_code
        
        self.logger.info('Websocket error in mic ' + str(self.mic_id) +' channel ' + str(self.channel))
        self.logger.info("Websocket error code: {}".format(error_code))
        self.logger.info('Websocket error ' + self.client.errorString())
        self.fastConnect = True
        if error_code == 11:
            self.window.statusbar.showMessage(
                'Connection to server timedout', 4000)
        else:
            self.window.statusbar.showMessage(
                'A server error occurred, try reconnecting for ' + self.speaker_name, 2000)
        self.customsignal.update_treeitem_background.emit(
            None, (255, 0, 0, 100), self.mic_id, self.channel)

    @pyqtSlot(object, str, str)
    def send_data(self, data, type_data, extra_arg):
        # self.client.sendTextMessage("keepalive")
        if type_data == 'text':
            self.client.sendTextMessage(data)
            if extra_arg == 'stopped':
                self.is_disconnected = True
                if self.reconnectTimer.isActive(): 
                    self.reconnectTimer.stop()
            if extra_arg == 'paused':
                self.is_paused = True
                if self.reconnectTimer.isActive(): 
                    self.reconnectTimer.stop()
            if extra_arg == 'reconnect':
                self.is_disconnected = False
                self.is_paused = False
        else:
            self.client.sendBinaryMessage(data)

    @pyqtSlot()
    def websocket_opened(self):
        endTime = timer()
        if self.lastError != None:
            arrayData = self.errorDict[self.lastError] 
            TimeTaken = endTime - arrayData[3]
            arrayData[2] =  arrayData[2] + TimeTaken
            self.lastError=None
            
        if self.lastServerError != None:
            arrayData = self.serverErrorDict[self.lastServerError]
            TimeTaken = endTime - arrayData[3]
            arrayData[2] =  arrayData[2] + TimeTaken
            self.lastServerError = None
            
            
            
        self.is_disconnected = False
        self.is_paused = False
        if self.reconnectTimer.isActive():
            self.reconnectTimer.stop()
        # self.websocket_timer.stop()
        self.customsignal.update_treeitem_background.emit(None, self.color, self.mic_id, self.channel)
        print('connection established mic: ' +str(self.mic_id) + ' channel ' + str(self.channel))
        self.logger.info('connection established mic: ' +str(self.mic_id) + ' channel ' + str(self.channel))
        self.customsignal.start_recording.emit(self.mic_id)
        
        # if self.start == None:
        #     print("start Timer")
        #     self.start = timer()
        
        # if self.currentoffset != 0:
        #     self.offset = self.offset + self.currentoffset
        #     self.currentoffset = 0
        #     print("current offset = " +str(self.offset))

    @pyqtSlot(str)
    def received_message(self, message):
        response = json.loads(str(message))
        # print(response)
        if "message" in response:
            if response['message'] == 'ready':
                self.is_connected = True
        if response['status'] == 0 or response['status'] == 200:
            # if self.is_connected == False:
            #     self.setConnectTimer.start(1000)
            # print("status"+ str(response['status']))
            if 'result' in response:
                trans = response['result']['hypotheses'][0]['transcript']
                if response['result']['final']:
                    # print >> sys.stderr, trans,
                    self.final_hyps.append(trans)
                    if trans != '<noise>.' and trans != '<v-noise>.':
                        segment_start = float(response['segment-start'])
                        segment_end = float(response['segment-start']) + float(response['segment-length'])
                        seg_start = float((self.countBlockfix + segment_start))
                        seg_end = float((self.countBlockfix + segment_end))
                        
                        self.customsignal.add_message.emit(trans.replace("\n", "\\n"), str(
                            self.mic_id), self.channel, self.icon, self.color, seg_start, seg_end,self.model)
                    print('\rFinal: ' + str(self.mic_id) + '%s' %
                          trans.replace("\n", "\\n"), file=sys.stderr)
                    
                    print("offset:" + str(self.countBlockfix) +" " + str(seg_start) +" " + str(seg_end))
                else:
                    print_trans = trans.replace("\n", "\\n")
                    if len(print_trans) > 80:
                        print_trans = "... %s" % print_trans[-76:]
                    if trans != '<noise>.' and trans != '<v-noise>.':
                        self.customsignal.update_message.emit(trans.replace(
                            "\n", "\\n"), str(self.mic_id), self.channel, self.icon, self.color)
                    # print('\rNot Final: ' + str(self.mic_id) + '%s' %print_trans, file=sys.stderr)
            if 'adaptation_state' in response:
                if self.save_adaptation_state_filename:
                    print("Saving adaptation state to %s" %
                          self.save_adaptation_state_filename, file=sys.stderr)
                    with open(self.save_adaptation_state_filename, "w+") as f:
                        f.write(json.dumps(response['adaptation_state']))
        else:
            print("Received error from server (status %d)" %response['status'], file=sys.stderr)
            self.logger.info("Received error from server (status %d)" %response['status'])
            

            if 'message' in response:
                if response['message'].split(" ", 1)[1].split(' \n')[0] == "Access Token doesn't exist. Contact admin to get detail!.":
                    self.window.statusbar.showMessage('Access token does not exist. Please provide a new access token.', 10000)
                print("Error message:",  response['message'], file=sys.stderr)
                self.logger.info("Error message:"  + response['message'])
                if response['status'] in self.serverErrorDict:
                    self.serverErrorDict[response['status']][1] = self.serverErrorDict[response['status']][1] + 1
                    self.serverErrorDict[response['status']][3] = timer()
                else:
                    self.serverErrorDict[response['status']] = [response['message'],1,0,timer()]
                self.lastServerError = response['status']
                self.serverErrorDict[response['status']].append(datetime.now())
                self.fastConnect=False
            if response['status'] == 9:
                self.is_disconnected = True
                if self.setConnectTimer.isActive(): 
                    self.setConnectTimer.stop()


    def get_full_hyp(self, timeout=60):
        return self.final_hyp_queue.get(timeout)
        

    def closed(self, code, reason=None):
        self.final_hyp_queue.put(" ".join(self.final_hyps))
        self.reconnectTimer.stop()
        self.logger.info('End session :' + str(self.mic_id) +' channel ' + str(self.channel))
        ## print Error Summary
        endTime = timer()
        if self.lastError != None:
            arrayData = self.errorDict[self.lastError] 
            TimeTaken = endTime - arrayData[3]
            arrayData[2] =  arrayData[2] + TimeTaken
            self.lastError=None
            
        if self.lastServerError != None:
            arrayData = self.serverErrorDict[self.lastServerError]
            TimeTaken = endTime - arrayData[3]
            arrayData[2] =  arrayData[2] + TimeTaken
            self.lastServerError = None
        self.logger.info("=======Error Summary=======")
        print(self.errorDict)
        print(self.serverErrorDict)
        for key in self.errorDict:
            errordata = self.errorDict[key]
            Errorcode = key
            ErrorString = errordata[0]
            numberOfEncounter = errordata[1]
            TotalDownTime = errordata[2]
            avgDownTime = errordata[2]/numberOfEncounter
            self.logger.info("Error Code {}".format(Errorcode))
            self.logger.info("Error String {}".format(ErrorString))
            self.logger.info("Number of times Error occur {}".format(numberOfEncounter))
            self.logger.info("Total Down Time {}".format(TotalDownTime))
            self.logger.info("Average Down Time {}".format(avgDownTime))
            self.logger.info(" ")
            self.logger.info("List of Date Time:")
            for i in range(len(errordata)-4):
                self.logger.info(errordata[i+4])
        for key in self.serverErrorDict:
            errordata = self.serverErrorDict[key]
            Errorcode = key
            ErrorString = errordata[0]
            numberOfEncounter = errordata[1]
            TotalDownTime = errordata[2]
            avgDownTime = errordata[2]/numberOfEncounter
            self.logger.info("Error Code {}".format(Errorcode))
            self.logger.info("Error String {}".format(ErrorString))
            self.logger.info("Number of times Error occur {}".format(numberOfEncounter))
            self.logger.info("Total Down Time {}".format(TotalDownTime))
            self.logger.info("Average Down Time {}".format(avgDownTime))
            self.logger.info(" ")
            self.logger.info("List of Date Time:")
            for i in range(len(errordata)-4):
                self.logger.info(errordata[i+4])

    @pyqtSlot()
    def websocket_disconnected(self):
        #dis_time = timer()
        if self.is_close == True: return
        self.is_connected = False
        self.logger.info("Websocket Discconnected: " + str(self.mic_id) +' channel ' + str(self.channel) + ' Trying time:' + str(self.reconnect_counter) +"\n")
        # if self.is_paused == True:
        #     if self.currentoffset == 0 and self.start != None:
        #         self.currentoffset =  self.pause - self.start
        
        # if self.is_disconnected == True:
        #     if self.currentoffset == 0 and self.start != None:
        #         self.currentoffset =  dis_time - self.start
                

        print('websocket disconnected, trying time:' + str(self.reconnect_counter))

        self.customsignal.update_treeitem_background.emit(None, (255, 0, 0, 100), self.mic_id, self.channel)
        # if socket is disconnect and not paused by user try to reconnect
        if self.reconnect_counter < 6000 and self.is_paused == False:
            # if self.start is not None:
                self.reconnect_counter = self.reconnect_counter + 1
                if not self.reconnectTimer.isActive(): 
                    if self.fastConnect:
                        self.reconnectTimer.start(50)
                    else:
                        self.reconnectTimer.start(60000)
                # self.reconnect()
        self.start=None

    def reconnect(self):
        print('reconnecting...')
        self.client.open(QUrl(self.url))
        # self.websocket_timer.start()
        
    def setConnect(self):
        self.is_connected = True
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        