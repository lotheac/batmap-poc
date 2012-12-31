#!/usr/bin/env python

from mapper import Area, Room
import unittest

class TestRoomParser(unittest.TestCase):
    '''Test correct parsing of room brief/desc/exits.'''

    def setUp(self):
        # make an area with five rooms:
        # o-o
        # |/ 
        # o-o o
        self.area = Area('test area')
        self.rooms = {
            'nw': 'nw.\nnorthwest room\nObvious exits are: s and e.',
            'ne': 'ne.\nnortheast room\nwith multiline desc\nObvious exits are: w and sw.',
            'sw': 'sw.\nsouthwest room\nObvious exits are: n, ne and e.',
            'se': 'se.\nsoutheast room\nObvious exit is: west.',
            'o': 'o.\norphan room\nThere are no obvious exits.',
        }
        for k, v in self.rooms.items():
            self.rooms[k] = Room.fromstring(self.area, v)

    def test_exits(self):
        self.assertEqual(self.rooms['nw'].exits, set(['south', 'east']))
        self.assertEqual(self.rooms['ne'].exits, set(['west', 'southwest']))
        self.assertEqual(self.rooms['sw'].exits, set(['north', 'northeast',
                                                      'east']))
        self.assertEqual(self.rooms['se'].exits, set(['west']))
        self.assertEqual(self.rooms['o'].exits, set())

    def test_brief(self):
        self.assertEqual(self.rooms['o'].brief, 'o')

    def test_desc(self):
        self.assertEqual(self.rooms['ne'].desc, 'northeast room\nwith multiline desc')

if __name__ == '__main__':
    unittest.main()
