# pylint: disable-msg=E0611
from __future__ import print_function
import sys
from PyQt4 import QtCore, QtGui
from documentwatcher import DocumentWatcher
from geometrywidget import GeometryWidget
from cadfileparser import FcadParser
from printcapturecontext import PrintCaptureContext
from svggenerator import SvgGenerator
from geometrygenerator import GeometryGenerator



class OpenSCAD2D(object):
    def __init__(self, filename):

        self.screen_width, self.screen_height = 800.0, 600.0

        self.file_generator = SvgGenerator()
        self.geometry_generator = GeometryGenerator(self.screen_width, self.screen_height)

        self.widget = None
        self.watcher = None

        self.loadFile(filename)

    def loadFile(self, filename):
        self.filename = filename

        if self.watcher:
            self.watcher.stop_monitor()
        self.watcher = DocumentWatcher(self.filename, self.on_file_change)
        self.watcher.monitor()

        self.parser = FcadParser(filename)

        self.update()

    def update(self):
        with PrintCaptureContext() as capture_context:
            self.parser = FcadParser(self.filename)
            ast, error = self.parser.parse()
            print("AST:", ast, ", Error:", error)

            if not error:
                data = self.geometry_generator.generate(ast)
            else:
                raise Exception(error)


        if self.widget:
            self.widget.setData(data, capture_context, error)

        return data, capture_context, error

    def run(self):
        app = QtGui.QApplication(sys.argv)
        app.setApplicationName("OpenSCAD2D")
        app.setQuitOnLastWindowClosed(True)
        app.setWindowIcon(QtGui.QIcon('../logo.png'))
        data, capture_context, error = self.update()
        self.widget = GeometryWidget(self.filename, data, capture_context, error, self.screen_width, self.screen_height, self.loadFile)

        sys.exit(app.exec_())

    def on_file_change(self):
        self.update()

if __name__ == "__main__":
    if len(sys.argv) <= 1:
        #print "no"
        program = OpenSCAD2D("../test/data/complex_example.fcad")
    else:
        program = OpenSCAD2D(sys.argv[1])

    program.run()

