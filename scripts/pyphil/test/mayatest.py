import maya.standalone
maya.standalone.initialize()

import maya.cmds as cmds
import unittest

class TestCase(unittest.TestCase):

    def tearDown(self):
        cmds.file(newFile=True, force=True)
