import sys
import os
from PyQt5 import QtGui
from PyQt5 import QtCore
import pyqtgraph as pg
import numpy as np

# Override the pg.ViewBox class to add custom
# implementations to the wheelEvent

class CustomViewBox(pg.ViewBox):
    sigMousePressed = QtCore.Signal(object)


    def __init__(self, *args, **kwds):
        pg.ViewBox.__init__(self, *args, **kwds)
        self.rect_item = None
        self.oldX = None
        #self.setMouseMode(self.RectMode)

    def wheelEvent(self, ev, axis=None):
        min = self.allChildren()[1].dataBounds(0)[0]
        max = self.allChildren()[1].dataBounds(0)[1]
        
        speed = ev.delta()/120
        x_range_min = self.viewRange()[0][0]
        x_range_max = self.viewRange()[0][1]
        x_range_min = x_range_min + speed*16000
        x_range_max = x_range_max + speed*16000
        self.setRange(rect=None, xRange=[x_range_min,x_range_max], yRange=None, padding=0, update=True, disableAutoRange=True)
    
    def mousePressEvent(self, event):
        if(self.rect_item != None):
            self.removeItem(self.rect_item)
        
        self.begin =self.mapToView(event.pos())
        self.end = self.mapToView(event.pos())

    def mouseMoveEvent(self, event):
        self.end = self.mapToView(event.pos())
        ymax = self.viewRange()[1][1]
        ymin = self.viewRange()[1][0]
        startX = self.begin.x()
        startY = self.begin.y()
        endX = self.end.x()
        endY = self.end.y()
        h = -(ymax) + ymin
        h = h*0.99
        if(self.rect_item != None):
            self.removeItem(self.rect_item)
        self.setLimits(yMax=ymax,yMin=ymin)
        self.rect_item = RectItem(QtCore.QRectF(startX, ymax, endX-startX, h))
        self.addItem(self.rect_item)

    def mouseReleaseEvent(self, event):
 
        if(self.begin == self.end):
            if(event.button() == QtCore.Qt.LeftButton ):
                self.oldX = None
                self.sigMousePressed.emit(self.begin)
                return
            else:
                return
        ymax = self.viewRange()[1][1]
        ymin = self.viewRange()[1][0]
        
        h = -(ymax) + ymin
        h = h*0.99
        self.setLimits(yMax=ymax,yMin=ymin)
        
        startX = self.begin.x()
        startY = self.begin.y()
        endX = self.end.x()
        endY = self.end.y()

        coor = []
        coor.append(self.begin)
        coor.append(self.end)
        
        self.oldX = [startX,endX]
        
        self.begin =self.mapToView(event.pos())
        self.end = self.mapToView(event.pos())



class RectItem(pg.GraphicsObject):
    def __init__(self, rect, parent=None):
        super().__init__(parent)
        self._rect = rect
        self.picture = QtGui.QPicture()
        self._generate_picture()

    @property
    def rect(self):
        return self._rect

    def _generate_picture(self):
        painter = QtGui.QPainter(self.picture)
        painter.setPen(pg.mkPen("w"))
        painter.setBrush(QtGui.QColor(30, 30, 30, 120))
        painter.drawRect(self.rect)
        painter.end()

    def paint(self, painter, option, widget=None):
        painter.drawPicture(0, 0, self.picture)

    def boundingRect(self):
        return QtCore.QRectF(self.picture.boundingRect())