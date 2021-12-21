# -*- coding: utf-8 -*-
"""
Created on Wed Jan 13 21:36:46 2021

@author: desmo
"""

import logging
import os.path

logger = logging.getLogger()
fhandler = logging.FileHandler(filename=os.path.dirname(__file__)+'/../Error.log', mode='a')
formatter = logging.Formatter(u'%(levelname)8s %(asctime)s %(message)s ')
fhandler.setFormatter(formatter)
logger.addHandler(fhandler)
logger.setLevel(logging.DEBUG)

logger.info("Disconnected")