import maya.OpenMaya as om

class ObjectError(RuntimeError):
    """
    ObjectError is used to communicate errors related to PyPhil objects.
    """
    pass

class NotExistError(ObjectError):
    """
    NotExistError is raised when an object or attribute does not exist
    or otherwise could not be identified or found.

    Its identifier attribute holds the identifier for which no object
    could be found, either a string or a OpenMaya MUuid.
    """
    def __init__(self, identifier):
        if isinstance(identifier, om.MUuid):
            msg = "object <{:s}> does not exist".format(identifier.asString())
        else:
            msg = "object '{:s}' does not exist".format(identifier)
        super(ObjectError, self).__init__(msg)
        self.identifier = identifier

class NotUniqueError(ObjectError):
    """
    NotUniqueError is raised when something cannot be identified uniquely.

    Its identifier attribute holds the identifier for which multiple objects
    were found, either a string or a OpenMaya MUuid.
    """
    def __init__(self, identifier):
        if isinstance(identifier, om.MUuid):
            msg = "identifier <{:s}> is not unique".format(identifier.asString())
        else:
            msg = "identifier '{:s}' is not unique".format(identifier)
        super(ObjectError, self).__init__(msg)
        self.identifier = identifier

class UnknownComponentError(AttributeError):
    """
    UnknownComponentError is raised when one or more unknown or unsupported
    naming convention components are accessed or referred to.

    The convention attribute holds the NamingConvention related to the error.
    The components attribute is a list of the unknown/unsupported components.
    """
    def __init__(self, convention, components):
        self.convention = convention
        if isinstance(components, list):
            if len(components) == 0:
                raise ValueError("UnknownComponentError created with an empty list")
            self.components = components
        else:
            self.components = [components]

        if len(self.components) == 1:
            msg = "component '{:s}' is undefined for {:s} naming convention".format(self.components[0], convention)
        else:
            components = ", ".join(["'"+str(c)+"'" for c in components])
            msg = "components {:s} are undefined for {:s} naming convention".format(components, convention)

        if convention.isNoConvention():
            msg += "; has a NamingConventionScope been setup?"

        super(AttributeError, self).__init__(msg)
