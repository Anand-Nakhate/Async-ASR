from PyQt5.QtCore import QObject
from PyQt5.QtCore import pyqtSignal as Signal


class Customsignal(QObject):
    add_message = Signal(str, str, int, object, object, float, float,str)
    update_message = Signal(str, str, int, object, object)
    update_summary = Signal(str)
    reconnect_websocket = Signal(str, str)
    update_treeitem_background = Signal(object, object, int, int)
    reconnect_counter = Signal()
    terminate_thread = Signal(object)
    stop_signal = Signal()
    start_signal = Signal()
    start_recording = Signal(int)
    update_speakers = Signal(str, str, int)
    delete_speakers = Signal(int, str)
    assign_speakers = Signal(str)
    updateHotKey = Signal(str)
