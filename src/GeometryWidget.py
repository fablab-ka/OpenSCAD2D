from PyQt4 import QtCore, QtGui

class GeometryWidget(QtGui.QWidget):
    def __init__(self):
        super(GeometryWidget, self).__init__()

        self.initUI()

    def initUI(self):

        self.text = u'Hello World'

        self.setGeometry(300, 300, 280, 170)
        self.setWindowTitle('Draw text')
        self.show()

    def paintEvent(self, event):

        qp = QtGui.QPainter()
        qp.begin(self)
        self.drawText(event, qp)
        qp.end()

    def drawText(self, event, qp):

        qp.setPen(QtGui.QColor(168, 34, 3))
        qp.setFont(QtGui.QFont('Decorative', 10))
        qp.drawText(event.rect(), QtCore.Qt.AlignCenter, self.text)

    def setData(self, data):
        self.data = data