import sys
import wx
import threading
import networkx as nx

try:
    import tf
    sys.stdout.output = tf.out
    sys.stderr.output = tf.err
except ImportError:
    pass

class MapFrame(wx.Frame):
    '''Frame that contains the entire UI.'''

    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, wx.ID_ANY, title=title)
        MapWindow(self)

class MapWindow(wx.Window):
    '''Window that contains the map graph.'''

    def __init__(self, *args, **kwargs):
        super(MapWindow, self).__init__(*args, **kwargs)
        self.SetBackgroundColour('WHITE')
        events = {
            wx.EVT_MOTION: self.motion,
            wx.EVT_SIZE:   self.resize,
        }
        for event, handler in events.items():
            self.Bind(event, handler)

    def resize(self, event):
        pass

    def motion(self, event):
        if event.Dragging() and event.LeftIsDown():
            print 'left mouse is down'

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

class Room(object):

    @classmethod
    def fromstring(cls, area, roomstr):
        brief, desc, exitstr = roomstr.split('\n')
        return cls(area, brief=brief, desc=desc, exitstr=exitstr)

    def __init__(self, area, brief=None, desc=None, exitstr=None):
        self.area = area
        self.brief = brief
        self.desc = None
        self.exits = set()
        if exitstr:
            self.add_exits(exitstr)

    def add_exits(self, exitstr):
        if not (exitstr.startswith('Obvious exits are: ') or
                exitstr.startswith('Obvious exit is: ')):
            return
        exits = exitstr.split(':')[1].rstrip('.').lstrip()
        exits = exits.replace(' and ', ', ')
        exits = exits.split(', ')
        self.exits.update(map(self._normalize_exit, exits))

    @staticmethod
    def _normalize_exit(s):
        exitnames = {
            'n': 'north',
            'e': 'east',
            'w': 'west',
            's': 'south',
            'ne': 'northeast',
            'nw': 'northwest',
            'se': 'southeast',
            'sw': 'southwest',
            'u': 'up',
            'd': 'down',
        }
        if s in exitnames:
            return exitnames[s]
        return s

class Area(nx.DiGraph):

    def __init__(self, name):
        super(Area, self).__init__(directed=True)
        self.name = name
