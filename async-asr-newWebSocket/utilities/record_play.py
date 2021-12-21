import pyaudio
import wave
from array import array
from struct import pack


def record():
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    RECORD_SECONDS = 5

    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, channels=CHANNELS,rate = RATE,input = True, frames_perbuffer=CHUNK)
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
    wf.setchannels(CHANNELS)
    wf.setsamplewidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

def play(file):
    CHUNK = 1024
    wf = wave.open(file, 'rb')
    p=pyaudio.PyAudio()
    stream = p.open(format = p.get_format_from_width(wf.getsamplewidth()),
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
