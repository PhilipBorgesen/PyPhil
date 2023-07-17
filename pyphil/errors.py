from typing import Union

import maya.OpenMaya as om

from .types import Identifier

__all__ = [
    "ObjectError",
    "NotExistError",
    "NotUniqueError",
]


class ObjectError(RuntimeError):
    """
    ObjectError is used to communicate errors related to PyPhil objects.
    """
    pass


class NotExistError(ObjectError):
    """
    NotExistError is raised when an object or attribute does not exist
    or otherwise could not be identified or found.
    """

    """
    The identifier for which no instance could be found.
    """
    identifier: Identifier

    def __init__(self, identifier: Identifier):
        if isinstance(identifier, om.MUuid):
            msg = f"object <{identifier.asString()}> does not exist"
        else:
            msg = f"object '{identifier}' does not exist"
        super(ObjectError, self).__init__(msg)
        self.identifier = identifier


class NotUniqueError(ObjectError):
    """
    NotUniqueError is raised when something cannot be identified uniquely.
    """

    """
    The identifier for which multiple instances were found.
    """
    identifier: Identifier

    def __init__(self, identifier: Identifier):
        if isinstance(identifier, om.MUuid):
            msg = f"identifier <{identifier.asString()}> is not unique"
        else:
            msg = f"identifier '{identifier}' is not unique"
        super(ObjectError, self).__init__(msg)
        self.identifier = identifier
