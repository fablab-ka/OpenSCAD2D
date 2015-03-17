from __future__ import print_function
import os
import svgwrite
from PySide import QtCore, QtGui
from PySide.QtCore import Qt
from PySide.QtGui import QMessageBox


class GeometryWidget(QtGui.QMainWindow, object):
    def __init__(self, filename, data, log_data, error, screen_width, screen_height, load_file_callback):
        super(GeometryWidget, self).__init__()

        self.filename = filename
        self.data = data
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.load_file_callback = load_file_callback
        self.isLoading = False
        palette = QtGui.QPalette()
        palette.setColor(QtGui.QPalette.Background, QtCore.Qt.white)
        self.setPalette(palette)
        self.logList = log_data
        self.current_error = error
        self.initUI()

    def openFile(self):
        self.filename = str(QtGui.QFileDialog.getOpenFileName(self, 'Open File', os.path.expanduser('~')))
        self.load_file_callback(self.filename)
        self.setWindowTitle('OpenSCAD2D - ' + os.path.basename(self.filename))

    def exportSvgFile(self):
        if not self.data:
            QMessageBox.about(self, "No Data loaded yet!")
            return

        svgFilename = str(QtGui.QFileDialog.getSaveFileName(self, 'Export SVG File', os.path.expanduser('~'), "*.svg"))

        drawing = svgwrite.Drawing(svgFilename, profile='tiny', size=('1220mm', '610mm'), viewBox=('0 0 1220 610'))
        group = drawing.add(drawing.g(id='geometries', stroke='black', fill='none'))

        for elem in self.data:
            if elem.count() > 0:
                path = drawing.path()

                first = True
                for p in elem:
                    if first:
                        first = False
                        path.push(['M', p.x(), p.y()])
                    else:
                        path.push(['L', p.x(), p.y()])

                group.add(path)
        drawing.save()

    def exportDxfFile(self):
        pass # TODO

    def createMenu(self):
        openAction = QtGui.QAction(QtGui.QIcon('open.png'), '&Open', self)
        openAction.setShortcut('Ctrl+O')
        openAction.setStatusTip('Open file')
        openAction.triggered.connect(self.openFile)

        exportSvgAction = QtGui.QAction(QtGui.QIcon('export.png'), 'Export &SVG', self)
        exportSvgAction.setShortcut('Ctrl+S')
        exportSvgAction.setStatusTip('Export SVG File')
        exportSvgAction.triggered.connect(self.exportSvgFile)

        exitAction = QtGui.QAction(QtGui.QIcon('exit.png'), '&Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(QtGui.qApp.quit)

        exportMenu = QtGui.QMenu('Export', self)
        exportMenu.addAction(exportSvgAction)

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(openAction)
        fileMenu.addMenu(exportMenu)
        fileMenu.addAction(exitAction)

        viewMenu = menubar.addMenu('&View')
        helpMenu = menubar.addMenu('&?')

    def initUI(self):
        self.setGeometry(300, 300, self.screen_width, self.screen_height)
        self.setWindowTitle('OpenSCAD2D - ' + os.path.basename(self.filename))

        self.centralWidget = QtGui.QWidget()
        self.setCentralWidget(self.centralWidget)

        dock = QtGui.QDockWidget("Console", self)
        dock.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea | QtCore.Qt.RightDockWidgetArea | QtCore.Qt.BottomDockWidgetArea)
        self.consoleWidget = QtGui.QTextBlock()

        log_data = ()
        if self.logList:
            log_data = self.logList
        self.logList = QtGui.QListWidget(dock)
        self.logList.addItems(log_data)
        dock.setWidget(self.logList)
        self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, dock)
        self.createMenu()

        self.show()


    def paintEvent(self, event):

        qp = QtGui.QPainter()
        qp.begin(self)

        qp.setPen(QtGui.QColor(Qt.black))
        if self.data:
            for elem in self.data:
                qp.drawPolyline(elem)
        if self.isLoading:
            self.drawLoading(event, qp)
        qp.end()



    def drawLoading(self, event, qp):
        qp.setPen(QtGui.QColor(168, 34, 3))
        qp.setFont(QtGui.QFont('Decorative', 10))
        qp.drawText(event.rect(), QtCore.Qt.AlignCenter, "Loading...")

    def setData(self, data, log_data, error):
        self.data = data
        if self.logList:
            self.logList.addItems(log_data)
        else:
            self.logList = log_data
        self.current_error = error
        self.updateGeometry()