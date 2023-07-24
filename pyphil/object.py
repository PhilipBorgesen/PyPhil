from typing import Optional, Union

import maya.cmds as cmds
import maya.OpenMaya as om

from .errors import NotUniqueError, NotExistError
# from pyphil.path import Path
from .types import PatternLike, Identifier


__all__ = ["Object"]


class MetaObject(type):

    def __call__(cls, x: om.MObject | PatternLike) -> "Object":
        """
        Creates a new Object wrapping the given OpenMaya object. If the argument
        x is not an OpenMaya MObject the call resolves to Object.from_name(x).

        Args:
            x: An OpenMaya object to wrap, or a pattern to invoke
               Object.from_name with.

        Returns:
            An Object representing the given or identified object.

        Raises:
            NotExistError:  If no object exist by the possibly given pattern x.
            NotUniqueError: If more than one object is identified by x.
        """
        if isinstance(x, om.MObject):
            obj = Object.__new__(Object)
            obj.__init__(x)
            return obj
        return Object.from_name(x)

    @property
    def world(self) -> "Object":
        """
        Returns an Object referencing the world node which all other DAG
        nodes are rooted under.

        Returns:
            An Object representing the world node.
        """
        return Object(om.MItDag().root())


class Object(object, metaclass=MetaObject):
    """
    Object references a Maya node without using its name. It supports certain
    convenience operations, most noticeably getting the current name of the
    potentially renamed or moved object for use with the Maya Python API.

    Example:

        from pyphil import Object
        import maya.cmds as cmds

        sphere = cmds.sphere(name="mySphere")[0]
        obj    = Object(sphere)
        name   = cmds.rename(sphere, "roundThing")
        group  = cmds.group(name, name="group", world=True)

        print(obj)           # prints "|group|roundThing"

    """

    _obj: om.MObject
    _node: om.MFnDependencyNode

    @classmethod
    def from_name(cls, name: PatternLike) -> "Object":
        """
        Returns an Object referencing the object identified by name.

        The name can be a partial path or contain wildcards but must identify
        a single object uniquely. Any name value given is attempted converted to
        a string before use.

        As a special case, if name is "<world>" then Object.world is returned.

        You can use Object(n) as a shorthand for Object.from_name(n).

        Args:
            name: A unique name or path to the object, either a string or an
                  object convertible to such by str(...).

        Returns:
            An Object representing the identified object.

        Raises:
            NotExistError:  If no object exist by the given name.
            NotUniqueError: If more than one object is identified by name.
        """
        if isinstance(name, Object):
            return name
        name = str(name)
        if name == "<world>" or name == ":<world>":
            return Object.world
        return Object(_query(name))

    @classmethod
    def from_uuid(cls, uuid: Union[str, om.MUuid]) -> "Object":
        """
        Returns an Object referencing the object with the given uuid.

        Args:
            uuid: The universally unique identifier of the object.

        Returns:
            An Object representing the object.

        Raises:
            NotExistError: If no object exist with the given uuid.
        """
        if isinstance(uuid, str):
            uuid = om.MUuid(uuid)
        elif not isinstance(uuid, om.MUuid):
            raise ValueError(f"uuid must be a string or of type {om.MUuid.__class__}")
        return Object(_query(uuid))

    def __init__(self, mobject: om.MObject):
        self._obj = mobject
        if mobject.hasFn(om.MFn.kDagNode):
            self._node = om.MFnDagNode(mobject)
        elif mobject.hasFn(om.MFn.kDependencyNode):
            self._node = om.MFnDependencyNode(mobject)
        else:
            raise NotImplementedError("Object currently only supports MFnDependencyNode nodes")

    def __eq__(self, other) -> bool:
        return isinstance(other, Object) and self._obj == other._obj

    def __ne__(self, other) -> bool:
        return not isinstance(other, Object) or self._obj != other._obj

    def __hash__(self):  # TODO: Use MObjectHandle.hashCode
        # MObject does not implement __hash__ so this is the best hash
        # we can provide in the general case. Names, paths, and UUIDs may
        # change so hashes of those cannot be used.
        return self._obj.apiType()

    def __str__(self) -> str:
        """
        __str__ is called by Python when a string representation of self is
        needed, e.g. when str(self) is called. The string representation is
        a path to the represented object or "<world>" if self represents the
        world object.
        """
        return self._str()

    def __repr__(self) -> str:
        return f'Object("{self._str()}")'

    def _str(self, short: bool = False) -> str:
        node = self._node
        if isinstance(node, om.MFnDagNode):
            if short:
                n = node.partialPathName()
            else:
                n = node.fullPathName()
        else:
            n = node.name()

        if n == "":  # Nodes have non-empty names, except the world node
            n = "<world>"

        return n

    # def path(self, short: bool = False) -> Path:
    #     """
    #     path returns a unique string-based identifier for the object as
    #     a PyPhil Path object. By default, the path will be in long form,
    #     that is self.path().root() == Path.world, given self represents
    #     a DAG node with world as an ancestor.
    #
    #     If short=True the path will instead be the shortest possible
    #     partial path that uniquely can identify the object.
    #
    #     :param short:  if True, the path will be in partial, short form.
    #     :returns:      a Path to the object.
    #     """
    #     return Path(self._str(short))  # skip checks done by Path.of

    # @property  # Only getter, no setter
    # def name(self) -> str:
    #     """
    #     :returns: the name of the object
    #     """
    #     return self._node.name()

    @property
    def uuid(self) -> str:
        """
        Returns the universally unique identifier (UUID) of the object.

        Returns:
            The uuid of the object
        """
        return self._node.uuid().asString()


def _query(identifier: Identifier) -> om.MObject:
    """
    Returns a reference to the OpenMaya node identified by identifier.

    Args:
        identifier: A name pattern or UUID uniquely identifying the node.

    Returns:
        A MObject uniquely matching the identifier.

    Raises:
        NotExistError:  If no node was identified by the identifier.
        NotUniqueError: If multiple nodes matched the identifier pattern.
    """
    # MObject is a reference to a Maya node
    ref = om.MObject()
    # Create an OpenMaya selection list
    selection = om.MSelectionList()
    try:
        # Add the node, identified by the identifier, to the selection.
        # If this succeeds the selection contains a reference to the node.
        selection.add(identifier)
        if selection.length() > 1:
            raise NotUniqueError(identifier)
        # Make ref point to the first (and only) node in the selection.
        selection.getDependNode(0, ref)
        return ref
    except RuntimeError as e:
        if not str(e).startswith("(kInvalidParameter)"):
            raise e  # Unknown error occurred

    # pattern is not unique or matches no object. Figure out which it is.

    if isinstance(identifier, om.MUuid) or len(cmds.ls(identifier)) == 0:
        raise NotExistError(identifier)
    else:
        raise NotUniqueError(identifier)
