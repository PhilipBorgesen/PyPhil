from typing import Optional

import maya.cmds as cmds
import unittest

import maya.standalone
maya.standalone.initialize()


class TestCase(unittest.TestCase):

    def setUp(self):
        """
        setUp is run before each test method, setting up a fresh Maya scene
        for the test to run isolated in.
        """
        self.loadScene(self.scene())
        self.sceneInit()

    def loadScene(self, scene: Optional[str]):
        """
        loadScene opens the Maya project denoted by scene. If scene is None
        a default Maya project is loaded, equivalent to what Maya loads when
        a new project is created.

        :param scene: File path to the Maya project to load.
        """
        if scene is None:
            cmds.file(newFile=True, force=True)
        else:
            cmds.file(scene, open=True, force=True)

    ##########################################
    # METHODS TO BE OVERRIDDEN IN SUBCLASSES #
    ##########################################

    def scene(self) -> Optional[str]:
        """
        scene returns the path to a Maya project to run each test in.
        Classes that derive from TestCase can override this method
        to load a scene that manually has been set up rather than doing
        all setup programmatically from scratch (see self.sceneInit()).

        By default, scene returns None, meaning that an empty default
        project should be used.
        """
        return None

    def sceneInit(self):
        """
        sceneInit is run after the Maya scene denoted by self.scene()
        has been loaded. Classes that derive from TestCase should
        override this method to set up the scene to fit their needs.
        """
        pass
