from typing import Iterable, List, Optional, Union

import maya.cmds as cmds
import maya.OpenMaya as om

from .errors import NotUniqueError, NotExistError
from .name import Name
from .types import PatternLike, Identifier


__all__ = ["Object"]


class Object(object):
    """
    Object references a Maya node without using its name. It supports certain
    convenience operations, most noticeably getting the current name of the
    potentially renamed or moved object for use with the Maya Python API.

    Example:

        from pyphil import Object
        import maya.cmds as cmds

        sphere = cmds.sphere(name="mySphere")[0]
        obj    = Object.from_name(sphere)
        name   = cmds.rename(sphere, "roundThing")
        group  = cmds.group(name, name="group", world=True)

        print(obj.name())    # prints "|group|roundThing"
        print(obj)           # prints "|group|roundThing"
        print(obj.parent())  # prints "|group"

    """

    _obj: om.MObject
    _node: om.MFnDependencyNode

    @classmethod
    def list(cls, iterable: Optional[Iterable[PatternLike]]) -> List["Object"]:
        """
        list returns a list of Objects representing all objects identified
        by patterns in iterable, which is a list, generator, or other Python
        type which can be iterated. Each pattern must map to a single object.

        As a special case, if iterable is None, list returns the empty list.

        :returns: a list of Objects representing the objects in iterable.

        :raises ObjectError: if any of the patterns failed to identify a single,
                             unique object.
        """
        if iterable is None:
            return []
        return [cls.from_name(name) for name in iterable]

    @classmethod
    def from_name(cls, name: PatternLike) -> "Object":
        """
        from_name returns an Object referencing the object identified by name.
        The name can be a partial path or contain wildcards but must identify
        a single object uniquely. Any name value given is attempted converted to
        a string before use.

        As a special case, if name is "<world>" then Object.world() is returned.

        :param name: is a unique name or path to the object, either a string
                     or an object with a reasonable __str__ implementation.
        :returns:    an Object representing the object.

        :raises NotExistError:  if no object exist by the given name.
        :raises NotUniqueError: if more than one object is identified by name.
        """
        if isinstance(name, Object):
            return name
        name = str(name)
        if name == "<world>" or name == ":<world>":
            return Object.world()
        return Object(_query(name))

    @classmethod
    def from_uuid(cls, uuid: Union[str, om.MUuid]) -> "Object":
        """
        from_uuid returns an Object referencing the object with the given uuid.

        :param uuid: is the universally unique identifier of the object.
        :returns:    an Object representing the object.

        :raises NotExistError: if no object exist with the given uuid.
        """
        if isinstance(uuid, str):
            uuid = om.MUuid(uuid)
        elif not isinstance(uuid, om.MUuid):
            raise ValueError(f"uuid must be a string or of type {om.MUuid.__class__}")
        return Object(_query(uuid))

    @classmethod
    def world(cls) -> "Object":
        """
        world returns an Object referencing the world node.

        :returns: an Object representing the world.
        """
        return Object(om.MItDag().root())

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

    def __hash__(self):
        # MObject does not implement __hash__ so this is the best hash
        # we can provide in the general case. Names, paths, and UUIDs may
        # change so hashes of those cannot be used.
        return self._obj.apiType()

    def __str__(self) -> str:
        """
        __str__ is called by Python when a string representation of self is needed, e.g.
        when str(self) is called. The string representation is the shortest unique name
        of the represented object or "<world>" if self represents the world object.
        """
        return self.name(string=True)

    def __repr__(self) -> str:
        return f'Object.from_name("{self.name(string=True)}")'

    def name(self, string: bool = False) -> Union[str, Name]:
        """
        name returns a unique string-based identifier for the object.
        By default, a pyphil Name object is returned, but if the string
        parameter is True a string of the shortest possible unique name
        is returned instead.

        If string=False and self represents a DAG node then the returned
        Name will be rooted at Name.world, that is self.name().root() ==
        Name.world. In other words, the return value will be a full path.

        As a special case, if string=True and self represents the world
        object then name returns "<world>". This is not a legal name but
        neither is "", the actual DAG path to the world object.

        :param string: if True, instead returns the name as string.
        :returns:      a Name describing the long name of the object.
        """
        node = self._node
        if isinstance(node, om.MFnDagNode):
            if string:
                n = node.partialPathName()
            else:
                n = node.fullPathName()
        else:
            n = node.name()

        if n == "":  # Nodes have non-empty names, except the world node
            n = "<world>"

        if string:
            return n

        return Name(n)  # skip checks done by Name.of

    def uuid(self) -> str:
        """
        uuid returns as string the universally unique identifier (UUID) of the
        object represented by self.

        :returns: the uuid of the object as string
        """
        return self._node.uuid().asString()

    def parent(self) -> Optional["Object"]:
        """
        parent returns the parent of the object if it has one, otherwise None.

        :returns: the parent of the node, or None
        """
        node = self._node
        if isinstance(node, om.MFnDagNode):
            if node.parentCount() > 0:
                return Object(node.parent(0))
        return None


def _query(identifier: Identifier) -> om.MObject:
    """
    _query returns a reference to the OpenMaya node identified by identifier.
    The identifier may be a string name pattern or an OpenMaya MUuid object.

    :param identifier: is a name pattern or UUID uniquely identifying the node.
    :returns:          a MObject uniquely matching the identifier.

    :raises NotExistError:  if no node was identified by the identifier.
    :raises NotUniqueError: if multiple nodes matched the identifier pattern.
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
