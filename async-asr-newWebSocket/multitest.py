import pyaudio
import time
import numpy as np
WIDTH = 2
CHANNELS = 4
RATE = 16000
CHUNK = 1600
p = pyaudio.PyAudio()
fulldata = np.array([])
left_frames = []
right_frames = []
all_frames = []
import wave


try:
    stream = p.open(format=pyaudio.paInt16,
                    channels=2,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)
    for i in range(0, int(RATE / CHUNK * 10)):
        data = stream.read(CHUNK)
        all_frames.append(data)
        data = np.fromstring(data, dtype=np.float16)
        data = np.reshape(data, (CHUNK, 2))
        leftdata = data[:, 0]
        rightdata = data[:, 1]
        left_frames.append(leftdata.tobytes())
        right_frames.append(rightdata.tobytes())
    print('oneended')
    stream1 = p.open(format=pyaudio.paInt16,
                    channels=2,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)
    for i in range(0, int(RATE / CHUNK * 10)):
        data = stream.read(CHUNK)
        all_frames.append(data)
        data = np.fromstring(data, dtype=np.float16)
        data = np.reshape(data, (CHUNK, 2))
        leftdata = data[:, 0]
        rightdata = data[:, 1]
        left_frames.append(leftdata.tobytes())
        right_frames.append(rightdata.tobytes())
    stream.stop_stream()
    stream.close()
    stream1.stop_stream()
    stream1.close()

    p.terminate()

    wf = wave.open('left.wav', 'wb')  # opening the file
    wf.setnchannels(1)
    wf.setsampwidth(2)
    wf.setframerate(16000)
    wf.writeframes(b''.join(left_frames))  # writing the data to be saved
    wf.close()

    wf = wave.open('right.wav', 'wb')  # opening the file
    wf.setnchannels(1)
    wf.setsampwidth(2)
    wf.setframerate(16000)
    wf.writeframes(b''.join(right_frames))  # writing the data to be saved
    wf.close()

    wf = wave.open('all.wav', 'wb')  # opening the file
    wf.setnchannels(2)
    wf.setsampwidth(2)
    wf.setframerate(16000)
    wf.writeframes(b''.join(all_frames))  # writing the data to be saved
    wf.close()
except KeyboardInterrupt:
    # wf = wave.open('left.wav', 'wb')  # opening the file
    # wf.setnchannels(1)
    # wf.setsampwidth(2)
    # wf.setframerate(44100)
    # wf.writeframes(b''.join(left_frames))  # writing the data to be saved
    # wf.close()

    # wf = wave.open('right.wav', 'wb')  # opening the file
    # wf.setnchannels(1)
    # wf.setsampwidth(2)
    # wf.setframerate(44100)
    # wf.writeframes(b''.join(right_frames))  # writing the data to be saved
    # wf.close()

    wf = wave.open('all.wav', 'wb')  # opening the file
    wf.setnchannels(1)
    wf.setsampwidth(2)
    wf.setframerate(44100)
    wf.writeframes(b''.join(all_frames))  # writing the data to be saved
    wf.close()