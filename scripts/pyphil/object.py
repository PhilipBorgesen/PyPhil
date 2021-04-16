import maya.cmds as cmds
import maya.OpenMaya as om

from pyphil.errors import *
from pyphil.name import Name

def _query(pattern):
    """
    _query returns a reference to the OpenMaya node identified by pattern.

    :param pattern: is an name pattern uniquely identifying the node.
    :raises NotExistError:  if no node matched the pattern.
    :raises NotUniqueError: if multiple nodes matched the pattern.
    """
    # MObject is a reference to a Maya node
    ref = om.MObject()
    # Create an OpenMaya selection list
    selection = om.MSelectionList()
    try:
        # Add the node, identified by the pattern, to the selection.
        # If this succeeds the selection contains a reference to the node.
        selection.add(pattern)
        if selection.length() > 1:
            raise NotUniqueError("identifier '{:s}' is not unique".format(pattern))
        # Make ref point to the first (and only) node in the selection.
        selection.getDependNode(0, ref)
        return ref
    except RuntimeError as e:
        if not str(e.message).startswith("(kInvalidParameter)"):
            raise e  # Unknown error occurred

    # pattern is not unique or matches no object. Figure out which it is.
    if cmds.objExists(pattern):
        raise NotUniqueError("identifier '{:s}' is not unique".format(pattern))
    else:
        raise NotExistError("object '{:s}' does not exist".format(pattern))

class Object:
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
        :raises ObjectError: if any of the patterns failed to identify a
                             single, unique object.
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
        :return: an Object representing the object.
        :raises NotExistError: if no object exist by the given name.
        :raises NotUniqueError: if more than one object is identified by name.
        """
        if isinstance(name, Object):
            return name
        return Object(_query(str(name)))

    def __init__(self, mobject):
        self._ref = mobject
        if mobject.hasFn(om.MFn.kDagNode):
            self._node = om.MFnDagNode(mobject)
        elif mobject.hasFn(om.MFn.kDependencyNode):
            self._node = om.MFnDependencyNode(mobject)
        else:
            self._node = None

    def __eq__(self, other):
        """
        __eq__ is called when self == other is evaluated.
        """
        return isinstance(other, Object) and self._ref == other._ref

    def __ne__(self, other):
        """
        __ne__ is called when self != other is evaluated.
        """
        return not isinstance(other, Object) or self._ref != other._ref

    def __nonzero__(self):
        """
        __nonzero__ is called when self is converted to boolean, such as
        the condition of an if statement.
        """
        return self._node is not None

    # Setup Python 3 version
    __bool__ = __nonzero__

    def __str__(self):
        """
        __str__ is called by Python when a string representation of self is needed, e.g.
        when str(self) is called. The string representation is the shortest unique name
        of the represented object.
        """
        return self.name(string=True)

    def __repr__(self):
        """
        __repr__ is called by Python when a machine-readable string representation of self
        is needed. The string representation is the shortest unique name of the represented
        object.
        """
        return self.name(string=True)

    def name(self, string=False):
        """
        name returns a unique string-based identifier for the object.
        By default a pyphil Name object is returned, but if the string
        parameter is True a string of the shortest possible unique name
        is returned instead.

        :param string: if True, instead returns the name as string.
        :returns: a Name describing the long name of the object.
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

        if string:
            return n

        return Name.of(n)

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
