import sys
import wx
import threading
import networkx as nx
import random
import math

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

    CARDINALS = {
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

    @classmethod
    def fromstring(cls, area, roomstr):
        parts = roomstr.split('\n')
        brief = parts[0].rstrip('.')
        # desc is everything except first and last line
        desc = '\n'.join(parts[1:-1])
        exitstr = parts[-1]
        return cls(area, brief=brief, desc=desc, exitstr=exitstr)

    def __init__(self, area, brief=None, desc=None, exitstr=None):
        self.area = area
        self.brief = brief
        self.desc = desc
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
        self.exits.update(map(Room.normalize_exit, exits))

    @staticmethod
    def normalize_exit(s):
        if s in Room.CARDINALS:
            return Room.CARDINALS[s]
        return s

    @staticmethod
    def cardinal_modifier(cardinal):
        exit = Room.normalize_exit(cardinal)
        if not exit in Room.CARDINALS.values():
            raise ValueError('{!r} not a cardinal direction'.format(exit))
        modifiers = {
            'north': (0, 1),
            'south': (0, -1),
            'east': (1, 0),
            'west': (-1, 0),
            'northwest': (-1, 1),
            'northeast': (1, 1),
            'southwest': (-1, -1),
            'southeast': (1, -1),
        }
        return modifiers[exit]

class Area(nx.DiGraph):

    def __init__(self, name):
        super(Area, self).__init__(directed=True)
        self.name = name

    def _random_node_position(self):
        maxpos = self.number_of_nodes()
        if not hasattr(self, '_random'):
            self._random = random.Random(self)
        return (self._random.randint(0, maxpos),
                self._random.randint(0, maxpos))

    def cardinal_positions(self):
        '''Return positions for rooms connected via exits in cardinal
        directions.'''
        pos = {}
        for edge, exit in nx.get_edge_attributes(self, 'exit').items():
            n1, n2 = edge
            if exit in Room.CARDINALS.values():
                if not n1 in pos:
                    # do we have any other edges that give an idea of where
                    # this node should go?
                    for neighbor, attrs in self.edge[n1].items():
                        if neighbor not in pos:
                            continue
                        direction = attrs.get('exit', None)
                        if direction in Room.CARDINALS.values():
                            pos[n1] = tuple(x - dx for x, dx in
                                            zip(pos[neighbor],
                                                Room.cardinal_modifier(direction)))
                            print 'placed', n1, 'has', neighbor, direction
                            break
                    # place randomly if still not placed
                    if not n1 in pos:
                        pos[n1] = self._random_node_position()
                        print 'placed', n1
                if not n2 in pos:
                    pos[n2] = tuple(x + dx for x, dx in zip(pos[n1],
                                                            Room.cardinal_modifier(exit)))
                    print 'placed', n2, 'to', exit, 'of', n1
        return pos
