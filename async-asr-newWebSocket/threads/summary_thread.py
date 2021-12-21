import os
from PyQt5.QtCore import QThread, QObject
from PyQt5.QtCore import pyqtSignal as SIGNAL
from requests_futures.sessions import FuturesSession
from concurrent.futures import as_completed


class SummaryThread(QThread):

    def __init__(self, reqsession, summarydata, customsignal):
        QThread.__init__(self)

        self.customsignal = customsignal
        self.summarydata = {"text": summarydata}
        self.header_data = {
            "API_KEY": os.environ.get('API_KEY'),
            "API_SECRET": os.environ.get('API_SECRET'),
            "number_ext_summary": str(1),
            "version": str(2)
        }
        self.req_session = reqsession

    def __del__(self):
        print('waiting')
        self.wait()

    def run(self):
        print('________________requestsent____________')
        req_future = self.req_session.post(
            'http://nlp-speechlab.southeastasia.cloudapp.azure.com/summarize/', headers=self.header_data, data=self.summarydata)
        result = ''
        for fut in as_completed([req_future]):
            result = result + 'Abstractive:\n'
            result = result + \
                fut.result().json()['Data']['summarize']['data']['only_abs']
            result = result + '\nExtractive:\n'
            result = result + \
                fut.result().json()['Data']['summarize']['data']['only_ext']
            self.customsignal.update_summary.emit(result)
