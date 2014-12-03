from cadfileparser import *
import sys
from documentwatcher import DocumentWatcher
from geometrywidget import GeometryWidget
from svggenerator import SvgGenerator
from cairogenerator import CairoGenerator
from PyQt4 import QtCore, QtGui


class OpenSCAD2D:
    def __init__(self, filename):
        self.parser = FcadParser(filename)
        self.file_generator = SvgGenerator()
        self.ui_generator = CairoGenerator()

        self.watcher = DocumentWatcher(filename, self.on_file_change)
        self.watcher.monitor()

        self.widget = None

    def update(self):
        ast = self.parser.parse()
        data = self.ui_generator.generate(ast)
        self.widget.setData(data)

    def run(self):
        self.show_ui()
        self.update()

    def on_file_change(self):
        self.update()

    def show_ui(self):
        app = QtGui.QApplication(sys.argv)
        self.widget = GeometryWidget()
        sys.exit(app.exec_())

if __name__ == "__main__":
    if len(sys.argv) <= 1:
        #print "no"
        program = OpenSCAD2D("../samples/sample.fcad")
        program.run()
    else:
        program = OpenSCAD2D(sys.argv[1])
        program.run()

