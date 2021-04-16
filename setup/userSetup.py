import maya.cmds as cmds

try:
    if not (cmds.about(batch=True) or cmds.commandPort(":4434", query=True)):
        cmds.commandPort(name=":4434")
except RuntimeError as e:
    import logging
    logging.warn("Failed to open command port: %s", e.message)
