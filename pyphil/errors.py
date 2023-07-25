import maya.OpenMaya as om

from .types import Identifier

__all__ = [
    "ObjectError",
    "InvalidObjectError",
    "NotExistError",
    "NotUniqueError",
]


class ObjectError(RuntimeError):
    """
    ObjectError is used to communicate errors related to PyPhil objects.
    """
    pass


class InvalidObjectError(ObjectError):
    """
    InvalidObject is raised when an invalid Object is attempted used.
    An Object obj is invalid if obj.is_valid() returns False.

    Attributes:
        object (Object): The Object that is invalid.
    """

    object: "Object"

    def __init__(self, obj: "Object"):
        msg = f"object {id(obj)} does not reference a valid Maya object; has it been deleted?"
        super(ObjectError, self).__init__(msg)
        self.object = obj


class NotExistError(ObjectError):
    """
    NotExistError is raised when an object does not exist or otherwise
    could not be identified or found.

    Attributes:
        identifier (Identifier): The identifier for which no instance could be found.
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

    Attributes:
        identifier (Identifier): The identifier for which multiple instances were found.
    """

    identifier: Identifier

    def __init__(self, identifier: Identifier):
        if isinstance(identifier, om.MUuid):
            msg = f"identifier <{identifier.asString()}> is not unique"
        else:
            msg = f"identifier '{identifier}' is not unique"
        super(ObjectError, self).__init__(msg)
        self.identifier = identifier
