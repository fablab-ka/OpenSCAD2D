import pywatch


class DocumentWatcher(pywatch.Watcher):
    def __init__(self, document, callback):
        pywatch.Watcher.__init__(self, [document])

        self.callback = callback

    def execute(self):
        if not self.callback is None:
            self.callback()
        else:
            print "[error] callback not defined"