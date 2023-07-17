import maya.cmds as cmds
try:
    port = ":4434"
    if not (cmds.about(batch=True) or cmds.commandPort(port, query=True)):
        cmds.commandPort(name=port)
        print(f"Opened command port {port}")
except RuntimeError as e:
    import logging
    logging.warning("Failed to open command port: %s", str(e))
