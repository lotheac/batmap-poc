import sys
import wx
import threading

try:
    import tf
    sys.stdout.output = tf.out
    sys.stderr.output = tf.err
except ImportError:
    pass

class MapFrame(wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, wx.ID_ANY, title=title, size=(200,100))

class GUIThread(threading.Thread):

    def __init__(self, *args, **kwargs):
        super(GUIThread, self).__init__(*args, **kwargs)
        self.daemon = True
        self.frame = None
        self._startup_lock = threading.Lock()
        self._startup_lock.acquire()

    def run(self):
        app = wx.App()
        self.frame = MapFrame(None, "tf batmap")
        self.frame.Show(True)
        self._startup_lock.release()
        app.MainLoop()

    def start(self):
        super(GUIThread, self).start()
        self._startup_lock.acquire()
