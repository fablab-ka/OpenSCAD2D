from cadfileparser import *
import sys
from documentwatcher import DocumentWatcher
from geometrywidget import GeometryWidget
from svggenerator import SvgGenerator
from geometrygenerator import GeometryGenerator
from PyQt4 import QtCore, QtGui


class OpenSCAD2D:
    def __init__(self, filename):
        self.filename = filename

        self.parser = FcadParser(filename)
        self.file_generator = SvgGenerator()
        self.geometry_generator = GeometryGenerator()

        self.watcher = DocumentWatcher(filename, self.on_file_change)
        self.watcher.monitor()

        self.widget = None

    def update(self):
        ast, error = self.parser.parse()
        print ast, error
        data = self.geometry_generator.generate(ast)
        if self.widget:
            self.widget.setData(data, error)
        return data, error

    def run(self):
        app = QtGui.QApplication(sys.argv)
        data, error = self.update()
        self.widget = GeometryWidget(self.filename, data, error)
        sys.exit(app.exec_())

    def on_file_change(self):
        self.update()

if __name__ == "__main__":
    if len(sys.argv) <= 1:
        #print "no"
        program = OpenSCAD2D("../samples/sample.fcad")
        program.run()
    else:
        program = OpenSCAD2D(sys.argv[1])
        program.run()

