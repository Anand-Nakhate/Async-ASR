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
import tempfile

from ws4py.client.threadedclient import WebSocketClient
from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5.QtCore import pyqtSignal as SIGNAL
from slugify import slugify


FORMAT = pyaudio.paInt16
CHANNELS = 1
# RATE = 44100
# CHUNK = 16000  # 100ms

# audio = pyaudio.PyAudio()


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


class MyClient(WebSocketClient):

    def __init__(self, mode, audiofile, url, wf, protocols=None, extensions=None, heartbeat_freq=None, byterate=32000,
                 save_adaptation_state_filename=None, send_adaptation_state_filename=None, mic_id=1, rate=None, icon=None, customsignal=None, meeting_name=None, speaker_name=None, color=None):
        super(MyClient, self).__init__(
            url, protocols, extensions, heartbeat_freq)

        self.final_hyps = []
        self.byterate = byterate
        self.final_hyp_queue = queue.Queue()
        self.save_adaptation_state_filename = save_adaptation_state_filename
        self.send_adaptation_state_filename = send_adaptation_state_filename
        self.isStop = False
        self.audio = pyaudio.PyAudio()
        self.audiofile = audiofile
        self.mode = mode
        self.mic_id = mic_id
        self.rate = rate
        self.chunk = int((1/4) * self.byterate)
        self.icon = icon
        self.customsignal = customsignal
        self.meeting_name = meeting_name
        self.speaker_name = speaker_name
        self.color = color
        self.last_color = 'RED'
        self.wf = wf

    @rate_limited(4)
    def send_data(self, data):
        self.send(data, binary=True)

    def opened(self):
        def send_data_to_ws():
            if self.send_adaptation_state_filename is not None:
                print("Sending adaptation state from %s" %
                      self.send_adaptation_state_filename, file=sys.stderr)
                try:
                    adaptation_state_props = json.load(
                        open(self.send_adaptation_state_filename, "r"))
                    self.send(json.dumps(
                        dict(adaptation_state=adaptation_state_props)))
                except:
                    e = sys.exc_info()[0]
                    print("Failed to send adaptation state: ", e, file=sys.stderr)

            print("Start transcribing... " + str(self.mic_id))
            if self.mode == 'stream':
                stream = self.audio.open(format=FORMAT, channels=CHANNELS,
                                         rate=self.rate, input=True,
                                         frames_per_buffer=self.chunk,
                                         input_device_index=self.mic_id,
                                         output=True,
                                         output_device_index=self.mic_id)
                while not self.isStop:
                    data = stream.read(
                        self.chunk, exception_on_overflow=False)
                    try:
                        self.send_data(data)  # send data
                        self.wf.writeframes(data)
                        if self.last_color == 'RED':
                            self.customsignal.update_treeitem_background.emit(
                                None, self.color, self.mic_id)
                            self.last_color = 'ORIGINAL'
                    except AttributeError:
                        self.customsignal.update_treeitem_background.emit(
                            None, (255, 0, 0, 100), self.mic_id)
                        self.customsignal.reconnect_websocket.emit(
                            self.mic_id, 'AUTO')
                        self.last_color = 'RED'
                        self.customsignal.reconnect_counter.emit()

                stream.stop_stream()
                stream.close()
                self.audio.terminate()
            elif self.mode == 'file':
                with open(self.audiofile, 'rb') as audiostream:
                    for block in iter(lambda: audiostream.read(int(self.byterate/4)), b""):
                        if self.isStop:
                            break
                        try:
                            self.send_data(block)
                            self.wf.writeframes(block)
                            if self.last_color == 'RED':
                                self.customsignal.update_treeitem_background.emit(
                                    None, self.color, self.mic_id)
                                self.last_color = 'ORIGINAL'
                        except AttributeError:
                            self.customsignal.update_treeitem_background.emit(
                                None, (255, 0, 0, 100), self.mic_id)
                            self.customsignal.reconnect_websocket.emit(
                                self.mic_id, 'AUTO')
                            self.last_color = 'RED'
                            self.customsignal.reconnect_counter.emit()

            print("Audio sent, now sending EOS: " +
                  str(self.mic_id), file=sys.stderr)
            try:
                self.send("EOS")
            except AttributeError:
                pass

        t = threading.Thread(target=send_data_to_ws)
        t.start()

    def received_message(self, m):
        response = json.loads(str(m))
        if response['status'] == 0:
            if 'result' in response:
                trans = response['result']['hypotheses'][0]['transcript']
                if response['result']['final']:
                    #print >> sys.stderr, trans,
                    self.final_hyps.append(trans)
                    if trans != '<noise>.' and trans != '<v-noise>.':
                        segment_start = float(response['segment-start'])
                        segment_end = response['segment-start'] + \
                            float(response['segment-length'])
                        self.customsignal.add_message.emit(trans.replace("\n", "\\n"), str(
                            self.mic_id), self.icon, self.color, segment_start, segment_end)

                    print('\rFinal: ' + str(self.mic_id) + '%s' %
                          trans.replace("\n", "\\n"), file=sys.stderr)
                else:
                    print_trans = trans.replace("\n", "\\n")
                    if len(print_trans) > 80:
                        print_trans = "... %s" % print_trans[-76:]
                    if trans != '<noise>.' and trans != '<v-noise>.':
                        self.customsignal.update_message.emit(trans.replace(
                            "\n", "\\n"), str(self.mic_id), self.icon, self.color)
                    print('\rNot Final: ' + str(self.mic_id) + '%s' %
                          print_trans, file=sys.stderr)
            if 'adaptation_state' in response:
                if self.save_adaptation_state_filename:
                    print("Saving adaptation state to %s" %
                          self.save_adaptation_state_filename, file=sys.stderr)
                    with open(self.save_adaptation_state_filename, "w+") as f:
                        f.write(json.dumps(response['adaptation_state']))
        else:
            print("Received error from server (status %d)" %
                  response['status'], file=sys.stderr)
            if 'message' in response:
                print("Error message:",  response['message'], file=sys.stderr)

    def get_full_hyp(self, timeout=60):
        return self.final_hyp_queue.get(timeout)

    def closed(self, code, reason=None):
        self.final_hyp_queue.put(" ".join(self.final_hyps))
