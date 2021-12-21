import configparser
import os
import pyaudio
import numpy as np
import audioop
import wave
import time
from slugify import slugify
from PyQt5.QtCore import QThread, QObject, QTimer
from PyQt5.QtCore import pyqtSignal as SIGNAL
from PyQt5.QtNetwork import QAbstractSocket
from timeit import default_timer as timer

FORMAT = pyaudio.paInt16


def rate_limited(maxPerSecond):
    minInterval = 1.0 / float(maxPerSecond)

    def decorate(func):
        lastTimeCalled = [0.0]

        def rate_limited_function(*args, **kargs):
            elapsed = time.perf_counter() - lastTimeCalled[0]
            leftToWait = minInterval - elapsed
            if leftToWait > 0:
                time.sleep(leftToWait)
            ret = func(*args, **kargs)
            lastTimeCalled[0] = time.perf_counter()
            return ret
        return rate_limited_function
    return decorate


class RecordThread(QThread):

    def __init__(self, totalchannels, samplingrate, mic_id, channel_thread, mode, silence_timeout):
        QThread.__init__(self)

        self.totalchannels = totalchannels
        self.samplingrate = samplingrate
        self.mic_id = mic_id
        self.audio = pyaudio.PyAudio()
        self.channel_thread = channel_thread
        self.isStop = False
        self.mode = mode
        self.chunk = int((1/4) * (2*self.samplingrate))
        self.silence_timeout = int(silence_timeout)
        self.keepalive_time = (self.silence_timeout - 3) * 1000
        self.keepalive_timer = QTimer()
        self.keepalive_timer.setInterval(self.keepalive_time)
        self.keepalive_timer.timeout.connect(self.keepalive_connection)
        self.keepalive_timer.start()


        self.isRecordEnabled = self.channel_thread[list(self.channel_thread.keys())[0]].filename is None
        if self.isRecordEnabled:
            config = configparser.ConfigParser()
            config.read('services.ini')

            self.chunksaving_time = int(config['ASR']['chunksaving_time']) * 1000
            self.chunksaving_timer = QTimer()
            self.chunksaving_timer.setInterval(self.chunksaving_time)
            self.chunksaving_timer.timeout.connect(self.chunksave_audio)
            self.chunksaving_timer.start()

    def run(self):
        if self.mode == 'stream':
            stream = self.audio.open(format=FORMAT, channels=self.totalchannels,
                                     rate=self.samplingrate, input=True,
                                     frames_per_buffer=self.chunk,
                                     input_device_index=self.mic_id)
            c = 0
            ## save channel data if error during record
            ## to write back data next loop
            backup_data = b""
            savingError = False
            while not self.isStop:
                # c =c +1
                data = self.reading_stream(stream)
                data = np.fromstring(data, dtype=np.float16)
                data = np.reshape(data, (self.chunk, self.totalchannels))   
                if (self.channel_thread[1].is_connected == False) : 
                    time.sleep(0.5)
                    continue
                for channel in range(1, self.totalchannels+1):
                    channel_data = data[:, channel-1].tobytes()
                    if self.samplingrate != self.channel_thread[channel].endpoint_sampling_rate:
                        channel_data = audioop.ratecv(channel_data, 2, 1, self.samplingrate, self.channel_thread[channel].endpoint_sampling_rate, None)
                        channel_data = channel_data[0]
                        
                    # if self.channel_thread[1].start == None:
                        
                    
                    if self.channel_thread[channel].client.state() != QAbstractSocket.UnconnectedState:
                        self.channel_thread[channel].send_signal.emit(channel_data, 'binary', 'data')
                        
                    try:
                        # error saving previously retry saving
                        if(savingError):
                            self.channel_thread[channel].wave_file.writeframes(backup_data)
                            savingError= False
                            backup_data = b""
                        if self.channel_thread[channel].is_disconnected == False and self.channel_thread[channel].is_paused == False:
                            # if c <50:
                            #     raise Exception(c)
                            if self.channel_thread[1].start == None:
                                print("start Timer")
                                self.channel_thread[1].start = timer()
                                self.channel_thread[1].countBlockfix = self.channel_thread[1].countBlock/2
                                print("offset Block = " + str(self.channel_thread[1].countBlockfix ))
                            self.channel_thread[1].countBlock = self.channel_thread[1].countBlock + 1
                            self.channel_thread[channel].wave_file.writeframes(channel_data)
                    except:
                        print("Error writing:" + str(c))
                        savingError= True
                        backup_data = backup_data + channel_data
                        

            stream.stop_stream()
            stream.close()
            self.audio.terminate()
            self.chunksaving_timer.stop()
            self.keepalive_timer.stop()

            print('eos sent')
            self.channel_thread[channel].send_signal.emit("EOS", 'text', 'stopped')
            self.channel_thread[channel].closed(0)

        elif self.mode == 'file':
            for file in self.channel_thread[1].filename:
                tempdata = None
                block_data = None
                with open(file, 'rb') as audiostream:
                    block = self.get_wav_data(audiostream)
                    while not self.isStop:
                        if (self.channel_thread[1].is_connected == False) : 
                            time.sleep(0.5)
                            continue
                        try:
                            if  self.channel_thread[1].client.state() ==3 and  self.channel_thread[1].is_disconnected == False and self.channel_thread[1].is_paused == False:
                                block_data = self.reading_block(block) 
                                if self.samplingrate != self.channel_thread[1].endpoint_sampling_rate:
                                    block_data = audioop.ratecv(block_data, 2, 1, self.samplingrate, self.channel_thread[1].endpoint_sampling_rate, None)
                                    block_data = block_data[0]
                                # block_data = audioop.tomono(block_data,2,0.5,0.5)
                                if self.channel_thread[1].start == None:
                                    print("start Timer")
                                    self.channel_thread[1].start = timer()
                                    self.channel_thread[1].countBlockfix = self.channel_thread[1].countBlock/4
                                    print("offset block = " + str(self.channel_thread[1].countBlockfix/2))
                                self.channel_thread[1].send_signal.emit(block_data, 'binary', 'data')
                                self.channel_thread[1].countBlock = self.channel_thread[1].countBlock + 1
                                
                                    # print(self.channel_thread[1].countBlock)
                                # self.channel_thread[1].wave_file.writeframes(
                                    # block_data)
                        except (AttributeError, StopIteration) as e:
                            if type(e) == AttributeError:
                                self.channel_thread[1].customsignal.update_treeitem_background.emit(
                                    None, (255, 0, 0, 100), self.channel_thread[1].ws.mic_id, self.channel_thread[1].ws.channel)
                                if self.channel_thread[1].reconnect_counter < 10:
                                    self.channel_thread[1].customsignal.reconnect_websocket.emit(
                                        str(self.channel_thread[1].ws.mic_id)+'-'+str(self.channel_thread[1].ws.channel), 'AUTO')
                                    self.channel_thread[1].customsignal.reconnect_counter.emit(
                                    )
                                self.channel_thread[1].ws.last_color = 'RED'
                            if type(e) == StopIteration:
                                print('file reading complete')
                                break
                        
            print('eos sent')

            self.keepalive_timer.stop()
            self.channel_thread[1].send_signal.emit("EOS", 'text', 'stopped')
            self.channel_thread[1].is_close = True
            self.channel_thread[1].closed(0)
            
    def get_wav_data(self, wavfile):
        for block in iter(lambda: wavfile.read(int((2*self.samplingrate)/4)), b""):
            yield block

    @rate_limited(4)
    def reading_block(self, block):
        return next(block)

    @rate_limited(4)
    def reading_stream(self, stream):
        return stream.read(
            self.chunk, exception_on_overflow=False)

    def keepalive_connection(self):
        for channel in range(1, self.totalchannels+1):
            if self.channel_thread[channel].client.state() != QAbstractSocket.UnconnectedState:
                self.channel_thread[channel].send_signal.emit(
                    "keepalive", 'text', 'keepalive')
                # self.channel_thread[channel].do_ping()
                

    def chunksave_audio(self):
        for channel in range(1, self.totalchannels+1):
            self.channel_thread[channel].currentpart = self.channel_thread[channel].currentpart + 1

            self.channel_thread[channel].wave_file.close()
            
            self.channel_thread[channel].wave_file = wave.open('./' + slugify(
            self.channel_thread[channel].meetingname+'-'+self.channel_thread[channel].speaker_name+'___' +str(self.channel_thread[channel].currentpart)) + '.wav', 'wb')
            self.channel_thread[channel].wave_file.setsampwidth(2)
            self.channel_thread[channel].wave_file.setframerate(self.channel_thread[channel].endpoint_sampling_rate)
            self.channel_thread[channel].wave_file.setnchannels(1)
