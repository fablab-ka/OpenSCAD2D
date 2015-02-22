import os
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import QPointF, Qt
from PyQt4.QtGui import QPolygonF, QPainterPath, QPolygon


class GeometryWidget(QtGui.QWidget):
    def __init__(self, filename, data, error, screen_width, screen_height):
        super(GeometryWidget, self).__init__()

        self.filename = filename
        self.data = data
        self.errorText = error if error else "Loading"
        self.screen_width = screen_width
        self.screen_height = screen_height

        self.initUI()

    def initUI(self):
        print "DATA", self.data
        self.setGeometry(300, 300, self.screen_width, self.screen_height)
        self.setWindowTitle('OpenSCAD2D - ' + os.path.basename(self.filename))
        self.show()


    def paintEvent(self, event):

        qp = QtGui.QPainter()
        qp.begin(self)

        qp.setPen(QtGui.QColor(Qt.black))
        if self.data:
            #TODO zoom & pan
            print list(self.data.coords)
            qp.drawPolyline(QPolygonF(map(lambda c: QPointF(c[0], c[1]), list(self.data.coords))))

        self.drawText(event, qp)
        qp.end()

    def drawText(self, event, qp):

        qp.setPen(QtGui.QColor(168, 34, 3))
        qp.setFont(QtGui.QFont('Decorative', 10))
        qp.drawText(event.rect(), QtCore.Qt.AlignCenter, self.errorText)

    def setData(self, data, error):
        self.data = data
        self.errorText = error