from pyphil.test import TestCase
from pyphil import Object
import maya.cmds as cmds

class TestObject(TestCase):

    def setUp(self):
        cmds.delete()

    def test_list_none(self):
        self.assertEqual(Object.list(None), [])
