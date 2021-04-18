from pyphil.errors import UnknownComponentError
from pyphil.convention import NamingConvention, NameComposition

class NoConvention(NamingConvention):
    """
    NoConvention is the default naming convention, that is none.
    NoConvention defines no name components and names are considered
    valid if they are legal Maya names (see NameComposition.is_valid).

    The only (intended) instance of NoConvention is

        NoConvention.instance

    which also is returned by NoConvention.__call__(), equivalent to

        NoConvention()
    """

    instance = None

    # noinspection PyMethodOverriding
    @classmethod
    def __call__(cls):
        return cls.instance

    def __str__(self):
        return "<no convention>"

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
        raise UnknownComponentError(NoConvention(), unsupported.keys())

NoConvention.instance = NoConvention.__new__(NoConvention)

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
        raise UnknownComponentError(NoConvention(), unsupported.keys())

    def get_component(self, component):
        raise UnknownComponentError(NoConvention(), component)
