import maya.cmds as cmds
import maya.OpenMaya as om

from pyphil.errors import *
from pyphil.name import Name

def _query(identifier):
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
        if not str(e.message).startswith("(kInvalidParameter)"):
            raise e  # Unknown error occurred

    # pattern is not unique or matches no object. Figure out which it is.

    if isinstance(identifier, om.MUuid) or len(cmds.ls(identifier)) == 0:
        raise NotExistError(identifier)
    else:
        raise NotUniqueError(identifier)

class Object(object):
    """
    Object references a Maya node without using its name. It supports certain
    convenience operations, most noticeably getting the current name of the
    potentially renamed or moved object for use with the Maya Python API.
    """

    @classmethod
    def list(cls, iterable):
        """
        list returns a list of Objects representing all objects identified
        by patterns in iterable, which is a list, generator, or other Python
        type which can be iterated. Each pattern must map to a signle object.

        As a special case, if iterable is None, list returns the empty list.

        :return: a list of Objects representing the objects in iterable.

        :raises ObjectError: if any of the patterns failed to identify a single,
                             unique object.
        """
        if iterable is None:
            return []
        return [cls.fromName(name) for name in iterable]

    @classmethod
    def fromName(cls, name):
        """
        fromName returns an Object referencing the object identified by name.
        The name can be a partial path or contain wildcards but must identify
        a single object uniquely. Any name value given is attempted converted to
        string before use.

        :param name: is a unique name or path to the object, either a string
                     or an object with a reasonable __str__ implementation.
        :return:     an Object representing the object.

        :raises NotExistError:  if no object exist by the given name.
        :raises NotUniqueError: if more than one object is identified by name.
        """
        if isinstance(name, Object):
            return name
        return Object(_query(str(name)))

    @classmethod
    def fromUUID(cls, uuid):
        """
        fromUUID returns an Object referencing the object with the given uuid.

        :param uuid: is the universally unique identifier of the object.
        :returns:    an Object representing the object.

        :raises NotExistError: if no object exist with the given uuid.
        """
        if isinstance(uuid, str):
            uuid = om.MUuid(uuid)
        elif not isinstance(uuid, om.MUuid):
            raise ValueError("uuid must be a string or of type {:s}".format(om.MUuid.__class__))
        return Object(_query(uuid))

    @classmethod
    def world(cls):
        """
        world returns an Object referencing the world node.

        :return: an Object representing the world.
        """
        return Object(om.MItDag().root())

    def __init__(self, mobject):
        self._ref = mobject
        if mobject.hasFn(om.MFn.kDagNode):
            self._node = om.MFnDagNode(mobject)
        elif mobject.hasFn(om.MFn.kDependencyNode):
            self._node = om.MFnDependencyNode(mobject)
        else:
            self._node = None

    def __eq__(self, other):
        return isinstance(other, Object) and self._ref == other._ref

    def __ne__(self, other):
        return not isinstance(other, Object) or self._ref != other._ref

    def __hash__(self):
        # MObject does not implement __hash__ so this is the best hash
        # we can provide in the general case. Names, paths, and UUIDs may
        # change so hashes of those cannot be used.
        return self._ref.apiType()

    def __nonzero__(self):
        return self._node is not None

    # Setup Python 3 version
    __bool__ = __nonzero__

    def __str__(self):
        """
        __str__ is called by Python when a string representation of self is needed, e.g.
        when str(self) is called. The string representation is the shortest unique name
        of the represented object or "<world>" if self represents the world object.
        """
        return self.name(string=True)

    def __repr__(self):
        return 'Object.fromName("{:s}")'.format(self.name(string=True))

    def name(self, string=False):
        """
        name returns a unique string-based identifier for the object.
        By default a pyphil Name object is returned, but if the string
        parameter is True a string of the shortest possible unique name
        is returned instead.

        As a special case, if string=True and self represents the world
        object then name returns "<world>". This is not a valid name
        but neither is "", the name actually held by the world object.

        :param string: if True, instead returns the name as string.
        :returns:      a Name describing the long name of the object.
        """
        node = self._node
        if node is None:
            return None  # Should never occur under normal usage

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

        return Name.of(n)

    def uuid(self):
        """
        uuid returns as string the universally unique identifier (UUID) of the object
        represented by self.

        :return: the uuid of the object as string
        """
        node = self._node
        if node is None:
            return None  # Should never occur under normal usage

        return node.uuid().asString()

    def parent(self):
        """
        parent returns the parent of the object if it has one, otherwise None.

        :returns: the parent of the node, or None
        """
        node = self._node
        if isinstance(node, om.MFnDagNode):
            if node.parentCount() > 0:
                return Object(node.parent(0))
        return None
