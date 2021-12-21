from PyQt5 import QtWidgets
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import QStyle, QStyleOptionSlider
from PyQt5.QtCore import QRect, QPoint, Qt


class LabelledSlider(QtWidgets.QWidget):
    def __init__(self, interval=1, orientation=Qt.Horizontal,
                 labels=None, parent=None):
        super(LabelledSlider, self).__init__(parent=parent)

        if orientation == Qt.Horizontal:
            self.layout = QtWidgets.QVBoxLayout(self)
        elif orientation == Qt.Vertical:
            self.layout = QtWidgets.QHBoxLayout(self)
        else:
            raise Exception("<orientation> wrong.")

        # gives some space to print labels
        self.left_margin = 10
        self.top_margin = 10
        self.right_margin = 10
        self.bottom_margin = 10

        self.layout.setContentsMargins(self.left_margin, self.top_margin,
                                       self.right_margin, self.bottom_margin)

        self.sl = QtWidgets.QSlider(orientation, self)

        if orientation == Qt.Horizontal:
            self.sl.setTickPosition(QtWidgets.QSlider.TicksBelow)
            self.sl.setMinimumWidth(300)  # just to make it easier to read
        else:
            self.sl.setTickPosition(QtWidgets.QSlider.TicksLeft)
            self.sl.setMinimumHeight(300)  # just to make it easier to read

        self.sl.setTickInterval(interval)
        self.sl.setSingleStep(1)
        self.sl.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #999999;
                height: 8px; /* the groove expands to the size of the slider by default. by giving it a height, it has a fixed size */
                background: white;
                margin: 2px 0;
            }
            
            QSlider::handle:horizontal {
                background: #f5f5f5;
                border: 1px solid #5c5c5c;
                height: 18px;
                width: 18px;
                margin: -6px 0; /* handle is placed by default on the contents rect of the groove. Expand outside the groove */
                border-radius: 3px;
            }
            QSlider::sub-page {
                background: #379ede;
            }
        """)

        self.layout.addWidget(self.sl)

    def paintEvent(self, e):
        super(LabelledSlider, self).paintEvent(e)

        style = self.sl.style()
        painter = QPainter(self)
        st_slider = QStyleOptionSlider()
        st_slider.initFrom(self.sl)
        st_slider.orientation = self.sl.orientation()

        length = style.pixelMetric(QStyle.PM_SliderLength, st_slider, self.sl)
        available = style.pixelMetric(
            QStyle.PM_SliderSpaceAvailable, st_slider, self.sl)

        for v, v_str in self.levels:
            # get the size of the label
            rect = painter.drawText(QRect(), Qt.TextDontPrint, v_str)

            if self.sl.orientation() == Qt.Horizontal:
                # I assume the offset is half the length of slider, therefore
                # + length//2
                x_loc = QStyle.sliderPositionFromValue(self.sl.minimum(),
                                                       self.sl.maximum(), v, available)+length//2

                # left bound of the text = center - half of text width + L_margin
                left = x_loc-rect.width()//2+self.left_margin
                bottom = self.rect().bottom()

                # enlarge margins if clipping
                if v == self.sl.minimum():
                    if left <= 0:
                        self.left_margin = rect.width()//2-x_loc
                    if self.bottom_margin <= rect.height():
                        self.bottom_margin = rect.height()

                    self.layout.setContentsMargins(self.left_margin,
                                                   self.top_margin, self.right_margin,
                                                   self.bottom_margin)

                if v == self.sl.maximum() and rect.width()//2 >= self.right_margin:
                    self.right_margin = rect.width()//2
                    self.layout.setContentsMargins(self.left_margin,
                                                   self.top_margin, self.right_margin,
                                                   self.bottom_margin)

            else:
                y_loc = QStyle.sliderPositionFromValue(self.sl.minimum(),
                                                       self.sl.maximum(), v, available, upsideDown=True)

                bottom = y_loc+length//2+rect.height()//2+self.top_margin-3
                # there is a 3 px offset that I can't attribute to any metric

                left = self.left_margin-rect.width()
                if left <= 0:
                    self.left_margin = rect.width()+2
                    self.layout.setContentsMargins(self.left_margin,
                                                   self.top_margin, self.right_margin,
                                                   self.bottom_margin)

            pos = QPoint(left, bottom)
            painter.drawText(pos, v_str)

        return
