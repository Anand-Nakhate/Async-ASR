import os
import sys
from utilities.utils import resource_path

os.environ['PATH'] = resource_path('./VideoLan') + os.pathsep + os.environ['PATH']
os.environ['PATH'] = resource_path('./VideoLan/VLC') + os.pathsep + os.environ['PATH']

os.environ['PYTHON_VLC_MODULE_PATH'] = resource_path('./VideoLan')
os.environ['PYTHON_VLC_LIB_PATH'] = resource_path('./VideoLan/VLC/libvlc.dll')

fileobj = open("logfile.log", "a")
fileobj.write('---------Session Started---------\n')
sys.stdout = fileobj
sys.stderr = fileobj