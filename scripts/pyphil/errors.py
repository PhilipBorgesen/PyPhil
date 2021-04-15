
class ObjectError(RuntimeError):
    """
    ObjectError is used to communicate errors related to PyPhil objects.
    """
    pass

class NotExistError(ObjectError):
    """
    NotExistError is raised when an object or attribute does not exist.
    """
    pass

class NotUniqueError(ObjectError):
    """
    NotUniqueError is raised when something cannot be identified uniquely.
    """
    pass
