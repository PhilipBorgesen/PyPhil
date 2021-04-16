
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
    pass

class NotUniqueError(ObjectError):
    """
    NotUniqueError is raised when something cannot be identified uniquely.
    """
    pass
