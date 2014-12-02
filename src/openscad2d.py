from cadfileparser import *
import sys
from documentwatcher import DocumentWatcher
from svggenerator import SvgGenerator
from cairogenerator import CairoGenerator
#import gtk


class OpenSCAD2D:
    def __init__(self, filename):
        self.parser = FcadParser(filename)
        self.file_generator = SvgGenerator()
        self.ui_generator = CairoGenerator()

        self.watcher = DocumentWatcher(filename, self.on_file_change)
        self.watcher.monitor()

        #self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)

    def update(self):
        ast = self.parser.parse()
        self.ui_generator.generate(ast)

    def run(self):
        self.show_ui()
        self.update()

    def on_file_change(self):
        self.update()

    def show_ui(self):
        #self.window.show()
        pass

if __name__ == "__main__":
    if len(sys.argv) <= 1:
        #print "no"
        program = OpenSCAD2D("../samples/sample.fcad")
        program.run()
    else:
        program = OpenSCAD2D(sys.argv[1])
        program.run()

