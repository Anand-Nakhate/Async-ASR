import pyaudio
import inspect
import os
import sys
import re
from PyQt5.QtCore import Qt, QFileInfo, QSettings
from PyQt5.QtWidgets import qApp, QLabel, QTreeWidget, QTreeWidgetItem, QTableWidget, QTableWidgetItem, QTextEdit, QPushButton, QTreeWidgetItemIterator
from PyQt5.QtGui import QFont


def getDeviceInfo():
    p = pyaudio.PyAudio()
    info = p.get_host_api_info_by_index(0)
    numdevices = info.get('deviceCount')
    device_list = []

    for i in range(0, numdevices):
        if (p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
            n = p.get_device_info_by_host_api_device_index(0, i).get('name')
            maxInputChannels = p.get_device_info_by_host_api_device_index(
                0, i).get('maxInputChannels')
            device_list.append("Input Device id " + str(i) + " - " + n.encode("utf8").decode(
                "cp950", "ignore") + ' - Max Channels: ' + str(maxInputChannels))

    p.terminate()

    return device_list

def getDeviceIndices():
    p = pyaudio.PyAudio()
    info = p.get_host_api_info_by_index(0)
    numdevices = info.get('deviceCount')
    device_indices = []

    for i in range(0, numdevices):
        if (p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
            device_indices.append(i)

    p.terminate()

    return device_indices



def getSupportedRate(device_id):
    p = pyaudio.PyAudio()
    devinfo = p.get_device_info_by_index(device_id)
    supported_rate = devinfo.get('defaultSampleRate')
    try:
        if p.is_format_supported(16000, input_device=devinfo.get('index'), input_channels=devinfo.get('maxInputChannels'), input_format=pyaudio.paInt16):
            supported_rate = 16000
    except ValueError:
        print('Device doesn\'t supports 16khz sampling rate. Using default sampling rate for device.')
        pass

    p.terminate()

    return int(supported_rate)


def str_to_list(list_string):
    if list_string == '[]':
        return []
    return list_string.strip('[]').replace("'", "").replace(" ", "").split(',')

# use the below restore and save functions to introduce UI restoration from pyqt data.


def restore(settings):
    finfo = QFileInfo(settings.fileName())

    if finfo.exists() and finfo.isFile():
        for w in qApp.allWidgets():
            mo = w.metaObject()

            if w.objectName() and not w.objectName().startswith("qt_") and w.objectName() != 'summary_box':
                settings.beginGroup(w.objectName())

                for i in range(mo.propertyCount(), mo.propertyOffset()-1, -1):
                    prop = mo.property(i)

                    if prop.isWritable():
                        name = prop.name()
                        val = settings.value(name, w.property(name))

                        if str(val).isdigit():
                            val = int(val)

                        w.setProperty(name, val)

                if isinstance(w, QLabel):
                    value = (settings.value('labeltext'))
                    w.setText(value)

                if isinstance(w, QPushButton):
                    value = (settings.value('buttontext'))
                    w.setText(value)

                if isinstance(w, QTableWidget):
                    name = w.objectName()
                    size = settings.beginReadArray(name)

                    j = 0

                    for i in range(size):
                        settings.setArrayIndex(i)

                        settings.beginReadArray('indexes')

                        settings.setArrayIndex(j)
                        speaker_icon = settings.value('indexes')
                        j += 1

                        settings.setArrayIndex(j)
                        timestamp = settings.value('indexes')
                        j += 1

                        settings.setArrayIndex(j)
                        messsage = settings.value('indexes')
                        j += 1

                        settings.setArrayIndex(j)
                        color = settings.value('indexes')
                        j += 1

                        settings.setArrayIndex(j)
                        start_endtime = settings.value('indexes')
                        j += 1

                        settings.setArrayIndex(j)
                        speaker_name = settings.value('indexes')
                        j = 0

                        settings.endArray()

                        speaker_item = QTableWidgetItem()
                        speaker_item.setTextAlignment(Qt.AlignCenter)
                        font = QFont()
                        font.setPointSize(15)
                        speaker_item.setFont(font)
                        speaker_item.setIcon(speaker_icon)
                        speaker_item.setData(Qt.UserRole, speaker_name)
                        speaker_item.setBackground(color)

                        speaker_message = QTableWidgetItem()
                        speaker_message.setText(messsage)
                        font = QFont()
                        font.setPointSize(15)
                        speaker_message.setFont(font)
                        speaker_message.setBackground(color)
                        speaker_message.setData(Qt.UserRole, start_endtime)

                        speaker_time = QTableWidgetItem()
                        speaker_time.setText(timestamp)
                        font = QFont()
                        font.setPointSize(15)
                        speaker_time.setFont(font)
                        speaker_time.setBackground(color)

                        w.setItem(i, 0, speaker_item)
                        w.setItem(i, 1, speaker_time)
                        w.setItem(i, 2, speaker_message)
                    settings.endArray()

                if isinstance(w, QTreeWidget):
                    name = w.objectName()
                    size = settings.beginReadArray(name)

                    j = 0

                    for i in range(size):
                        settings.setArrayIndex(i)

                        settings.beginReadArray('indexes')

                        settings.setArrayIndex(j)
                        speaker_icon = settings.value('indexes')
                        j += 1

                        settings.setArrayIndex(j)
                        speaker_text = settings.value('indexes')
                        j += 1

                        settings.setArrayIndex(j)
                        color = settings.value('indexes')
                        j = 0

                        settings.endArray()

                        item_0 = QTreeWidgetItem(w)
                        item_0.setText(0, speaker_text)
                        font = QFont()
                        font.setPointSize(15)
                        item_0.setFont(0, font)
                        item_0.setIcon(0, speaker_icon)
                        item_0.setBackground(0, color)
                    settings.endArray()

                settings.endGroup()


def save(settings):
    for w in qApp.allWidgets():
        mo = w.metaObject()

        if w.objectName() and not w.objectName().startswith("qt_") and w.objectName() != 'summary_box':
            settings.beginGroup(w.objectName())

            for i in range(mo.propertyCount()):
                prop = mo.property(i)
                name = prop.name()

                if prop.isWritable():
                    settings.setValue(name, w.property(name))

            if isinstance(w, QLabel):
                settings.setValue('labeltext', w.text())

            if isinstance(w, QPushButton):
                settings.setValue('buttontext', w.text())

            if isinstance(w, QTableWidget):
                settings.beginWriteArray(w.objectName())

                j = 0

                for i in range(w.rowCount()):
                    settings.setArrayIndex(i)

                    settings.beginWriteArray('indexes')

                    settings.setArrayIndex(j)
                    speaker_icon = w.item(i, 0).icon()
                    settings.setValue('indexes', speaker_icon)
                    j += 1

                    settings.setArrayIndex(j)
                    t_stamp = w.item(i, 1).text()
                    settings.setValue('indexes', t_stamp)
                    j += 1

                    settings.setArrayIndex(j)
                    message = w.item(i, 2).text()
                    settings.setValue('indexes', message)
                    j += 1

                    settings.setArrayIndex(j)
                    color = w.item(i, 2).background()
                    settings.setValue('indexes', color)
                    j += 1

                    settings.setArrayIndex(j)
                    start_endtime = w.item(i, 2).data(Qt.UserRole)
                    settings.setValue('indexes', start_endtime)
                    j += 1

                    settings.setArrayIndex(j)
                    speaker_name = w.item(i, 0).data(Qt.UserRole)
                    settings.setValue('indexes', speaker_name)
                    j = 0

                    settings.endArray()
                settings.endArray()

            if isinstance(w, QTreeWidget):
                settings.beginWriteArray(w.objectName())

                it = QTreeWidgetItemIterator(w)

                i = 0
                j = 0

                while it.value():
                    settings.setArrayIndex(i)

                    settings.beginWriteArray('indexes')

                    settings.setArrayIndex(j)
                    settings.setValue('indexes', it.value().icon(0))
                    j += 1

                    settings.setArrayIndex(j)
                    settings.setValue('indexes', it.value().text(0))
                    j += 1

                    settings.setArrayIndex(j)
                    settings.setValue('indexes', it.value().background(0))
                    j = 0

                    settings.endArray()

                    it += 1
                    i += 1
                settings.endArray()
            settings.endGroup()


# taken from srt library (https://github.com/cdown/srt/blob/develop/srt.py#L182)
SECONDS_IN_HOUR = 3600
SECONDS_IN_MINUTE = 60
HOURS_IN_DAY = 24
MICROSECONDS_IN_MILLISECOND = 1000


def timedelta_to_srt_timestamp(timedelta_timestamp):
    hrs, secs_remainder = divmod(timedelta_timestamp.seconds, 3600)
    hrs += timedelta_timestamp.days * 24
    mins, secs = divmod(secs_remainder, 60)
    msecs = timedelta_timestamp.microseconds // 1000
    return "%02d:%02d:%02d,%03d" % (hrs, mins, secs, msecs)


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.normpath(os.path.join(base_path, relative_path))


def write_to_textgrid(speaker_data, speaker):
    log = 'File type = "ooTextFile"\nObject class = "TextGrid"\n\n'

    textgrid_start = str(speaker_data[0][0][0])
    textgrid_end = str(speaker_data[0][-1][1])
    messages = speaker_data[0]
    speakers = {}

    for message in messages:
        if speakers.get(message[3], None) is None:
            speakers[message[3]] = []
        speakers[message[3]].append(message)

    log = log + 'xmin = ' + textgrid_start + '\n'
    log = log + 'xmax = ' + textgrid_end + '\n'
    log = log + 'tiers? <exists>\nsize = ' + str(len(speakers)) + '\nitem []:'

    for index, speaker in enumerate(speakers):
        log = log + '\n\titem [' + str(index+1) + ']:\n\t\tclass = "IntervalTier"\n\t\tname = "' + speaker + \
            '"\n\t\txmin = ' + str(speakers[speaker][0][0]) + '\n\t\txmax = ' + \
            str(speakers[speaker][-1][1]) + \
            '\n\t\tintervals: size = ' + str(len(speakers[speaker]))

        for index, message in enumerate(speakers[speaker]):
            log = log + '\n\t\tintervals [' + str(index + 1) + ']:'
            log = log + '\n\t\t\txmin = ' + message[0]
            log = log + '\n\t\t\txmax = ' + message[1]
            log = log + '\n\t\t\ttext = "' + message[2] + '"'

    return log

def cleanhtml(raw_html):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext

def getColorCode(entity):
    if entity == "PERSON":
        return "red"
    if entity == "GPE":
        return "green"
    if entity == "ORG":
        return "blue"
    if entity == "DATE":
        return "yellow"
    if entity == "CARDINAL":
        return "cyan"
    return "magenta"

def insert_str( index,string, str_to_insert):
    return string[:index] + str_to_insert + string[index:]
    
def model_selector(language_choice, config):
    print(language_choice)
    # if language_choice == 'english_16000':
    #     uri = config['ASR']['ip_english_16k']
    # elif language_choice == 'mandarin_16000':
    #     uri = config['ASR']['ip_mandarin_16k']
    # elif language_choice == 'english-mandarin_16000':
    #     uri = config['ASR']['ip_eng_mandarin_16k']
    # elif language_choice == 'english-malay_16000':
    #     uri = config['ASR']['ip_eng_malay_16k']
    # if language_choice == 'english_8000':
    #     uri = config['ASR']['ip_english_8k']
    # elif language_choice == 'mandarin_8000':
    #     uri = config['ASR']['ip_mandarin_8k']
    # elif language_choice == 'english-mandarin_8000':
    #     uri = config['ASR']['ip_eng_mandarin_8k']
    # elif language_choice == 'english-malay_8000':
    #     uri = config['ASR']['ip_eng_malay_8k']

    if language_choice == 'english_16000':
        model  = config['ASR']['english_16k']   # eng_closetalk
        
    elif language_choice == 'mandarin_16000':
        model = config['ASR']['mandarin_16k']   #mandarin_closetalk
        
    elif language_choice == 'english-mandarin_16000':
        model = config['ASR']['eng_mandarin_16k']   # cs_closetalk
        
    elif language_choice == 'english-malay_16000':  
        model = config['ASR']['eng_malay_16k']      # engmalay_closetalk
        
    if language_choice == 'english_8000':
        model = config['ASR']['english_8k']     #eng_telephony
        
    elif language_choice == 'mandarin_8000':
        model = config['ASR']['mandarin_8k']    #mandarin_telephony
    #elif language_choice == 'english-mandarin_8000':
        # = config['ASR']['ip_eng_mandarin_8k']
    #elif language_choice == 'english-malay_8000':
        #uri = config['ASR']['ip_eng_malay_8k']


    return model
