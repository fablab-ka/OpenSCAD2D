import os
from PyQt4 import QtCore, QtGui

class GeometryWidget(QtGui.QWidget):
    def __init__(self, filename, data, error):
        super(GeometryWidget, self).__init__()

        self.filename = filename
        self.data = data
        self.errorText = error if error else "Loading"

        self.initUI()

    def initUI(self):
        print "DATA", self.data
        self.setGeometry(300, 300, 800, 600)
        self.setWindowTitle('OpenSCAD2D - ' + os.path.basename(self.filename))
        self.show()

    def paintEvent(self, event):

        qp = QtGui.QPainter()
        qp.begin(self)
        self.drawText(event, qp)
        qp.end()

    def drawText(self, event, qp):

        qp.setPen(QtGui.QColor(168, 34, 3))
        qp.setFont(QtGui.QFont('Decorative', 10))
        qp.drawText(event.rect(), QtCore.Qt.AlignCenter, self.errorText)

    def setData(self, data, error):
        self.data = data
        self.errorText = error