import logging

import maya.cmds as cmds

try:
    if not cmds.commandPort(":4434", query=True):
        cmds.commandPort(name=":4434")
except RuntimeError as e:
    logging.warn("Failed to open command port: {:s}" % e.message)
