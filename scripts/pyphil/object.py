import maya.cmds as cmds
import maya.OpenMaya as om

from errors import *

def _query(name):
    """
    _query returns a reference to the OpenMaya node identified by name.

    :param name: is an identifier uniquely identifying the node.
    :raises NotExistError: if no node could be found with the name.
    :raises NotUniqueError: if multiple nodes could be found with the name.
    """
    # MObject is a reference to a Maya node
    ref = om.MObject()
    # Create an OpenMaya selection list
    selection = om.MSelectionList()
    try:
        # Add the node, identified by its name, to the selection.
        # If this succeeds the selection contains a reference to the node.
        selection.add(name)
        # Make ref point to the first (and only) node in the selection.
        selection.getDependNode(0, ref)
        return ref
    except RuntimeError as e:
        if not str(e.message).startswith("(kInvalidParameter)"):
            raise e  # Unknown error occurred

    # name is not unique or it does not exist. Figure out which it is.
    if cmds.objExists(name):
        raise NotUniqueError("identifier '{:s}' is not unique".format(name))
    else:
        raise NotExistError("object '{:s}' does not exist".format(name))

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
        by names in iterable, which is a list, generator, or other Python type
        which can be iterated.

        As a special case, if iterable is None, list returns the empty list.

        :return: a list of Objects representing the objects in iterable
        :raises ObjectError: if any of the objects could not be identified uniquely
        """
        if iterable is None:
            return []
        return [cls.fromName(name) for name in iterable]

    @classmethod
    def fromName(cls, name):
        """
        fromName returns an Object referencing the object identified by name.

        :param name: is a unique name or path to the object
        :return: an Object representing the object
        :raises NotExistError: if no object exist by the given name
        :raises NotUniqueError: if more than one object is identified by name
        """
        if isinstance(name, Object):
            return name
        return Object(_query(name))

    def __init__(self, mobject):
        self._ref = mobject
        # Assume mobject is a DAG node
        self._dag = om.MFnDagNode()
        self._dag.setObject(om.MDagPath.getAPathTo(mobject))

    def _node(self):
        """
        :returns: the underlying Maya node as a dependency node
        """
        if not hasattr(self, "_depNode"):
            self._dependencyNode = om.MFnDependencyNode()
            self._dependencyNode.setObject(self._ref)
        return self._dependencyNode

    def name(self, long=False):
        """
        name returns a string that uniquely identifies the object.
        By default the shortest possible unique identifier is returned.

        :param long: if long is True, the long name of the object is returned instead.
        :returns: the Maya Python name of the object
        """
        if self.isDAG():
            # if node is a DAG node that exists...
            if long:
                return self._dag.fullPathName()
            return self._dag.partialPathName()
        else:
            return self._node().name()

    def isDAG(self):
        """
        isDAG returns whether the object represents a DAG node.
        DAG nodes include groups, transforms, shapes, and other objects shown
        in the Maya Outliner.

        :return: True if the object is a DAG object
        """
        return self._dag.dagPath().isValid()

    def _requireDAG(self):
        if not self.isDAG():
            raise TypeError("object '{:s}' is not a DAG object".format(self))

    def __repr__(self):
        """
        __repr__ is called by Python when a machine-readable string representation
        of self is needed, e.g. when str(self) is called.
        The string representation is the shortest unique name of the represented object.
        """
        return self.name(long=False)

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

    def parent(self):
        """
        parent returns the parent of the object, given that it is DAG node.
        If the DAG node has no parent, None is returned.

        :returns: the parent of the DAG node, or None
        :raises TypeError: if the object is not a DAG node
        """
        self._requireDAG()
        if self._dag.parentCount() == 0:
            return None
        return Object(self._dag.parent(0))
