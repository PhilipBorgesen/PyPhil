from pyphil.errors import UnknownComponentError
from pyphil.convention.core import NamingConvention, NameComposition

class NoConvention(NamingConvention):
    """
    NoConvention is the default naming convention, that is, none.
    NoConvention defines no name components and names are considered
    valid if they are legal Maya names (see NameComposition.is_valid).

    NOTE: This class definition is shadowed by a variable declaration.
          The variable "NoConvention" refers to an object of this class.
    """

    #########################################
    # IMPLEMENTATIONS OF BASE CLASS METHODS #
    #########################################

    def decompose(self, name):
        name = str(name)
        if name == "":
            raise ValueError("invalid name ''; empty string forbidden")
        return NoComposition(name)

    def compose(self, **unsupported):
        if len(unsupported) == 0:
            raise ValueError("The composition of zero components is undefined")
        raise UnknownComponentError(NoConvention, unsupported.keys())

# Shadow the class definition with an instance of it, thereby creating a singleton.
NoConvention = NoConvention()

class NoComposition(NameComposition):

    def __init__(self, name):
        self._name = name

    #########################################
    # IMPLEMENTATIONS OF BASE CLASS METHODS #
    #########################################

    def name(self):
        return self._name

    def replace(self, **unsupported):
        if len(unsupported) == 0:
            return self
        raise UnknownComponentError(NoConvention, unsupported.keys())

    def get_component(self, component):
        raise UnknownComponentError(NoConvention, component)
