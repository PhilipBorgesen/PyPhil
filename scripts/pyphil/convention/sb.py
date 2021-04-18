from pyphil.errors import UnknownComponentError
from pyphil.convention import NamingConvention, NameComposition

class SBConvention(NamingConvention):
    """
    SBConvention denotes the following naming scheme:

        <side>_<module>_<basename>_<desc>_<type>

    The <side>, <module>, <basename>, and <type> components are required
    for a name to be considered valid under SBConvention. The possible
    values for <side>, <module>, and <type> are given by the
    sides, modules, and types attributes of SBConvention. The values must
    match exactly to be considered valid but other casings can be handled
    by SBConvention as well.

    <basename> is a single word that may consist of the letters a-z, A-Z,
    and the digits 0-9.

    <desc> is optional. When present it consists of one or more letters a-z,
    A-Z, underscores, and the digits 0-9.

    When a component is missing, the trailing underscore should also be
    absent. When fewer than four components (the minimum for a valid name)
    are present, SBConvention will attempt to label each the best it can
    based on the possible values for <side>, <module>, and <type>.

    The only (intended) instance of SBConvention is

        SBConvention.instance

    which also is returned by SBConvention.__call__(), equivalent to

        SBConvention()
    """

    instance = None

    # TODO: Complete these sets
    sides   = {"R", "L", "C"}  # right, left, center; all uppercase
    modules = {"arm", "leg"}   # all lowercase
    types   = {"FK", "GEO", "GRP", "IK", "JNT"}  # all uppercase

    # noinspection PyMethodOverriding
    @classmethod
    def __call__(cls):
        return cls.instance

    def __str__(self):
        return "<sb convention>"

    #########################################
    # IMPLEMENTATIONS OF BASE CLASS METHODS #
    #########################################

    def decompose(self, name):
        if isinstance(name, SBName):
            return name
        if name == "":
            raise ValueError("invalid name ''; empty string forbidden")
        return SBName(str(name))

    def compose(self, side=None, module=None, basename=None, desc=None, type=None, **unsupported):
        if len(unsupported) > 0:
            raise UnknownComponentError(SBConvention(), unsupported.keys())
        # Ensure that values composed from scratch are valid
        if side is None:
            raise ValueError("<side> component is required")
        if module is None:
            raise ValueError("<module> component is required")
        if basename is None:
            raise ValueError("<basename> component is required")
        if type is None:
            raise ValueError("<type> component is required")
        if desc is not None:
            desc = str(desc)
        return SBName(str(side), str(module), str(basename), desc, str(type))

SBConvention.instance = SBConvention.__new__(SBConvention)

class SBName(NameComposition):

    def __init__(self, name=None, side=None, module=None, basename=None, desc=None, type=None):
        self._decomposed = name is None
        # Either name or the components (except desc) must be given
        self._name     = name
        self._side     = side
        self._module   = module
        self._basename = basename
        self._desc     = desc
        self._type     = type

    ############################
    # COMPONENT GETTER METHODS #
    ############################

    def side(self):
        if not self._decomposed:
            self._decompose()
        return self._side

    def module(self):
        if not self._decomposed:
            self._decompose()
        return self._module

    def basename(self):
        if not self._decomposed:
            self._decompose()
        return self._basename

    def description(self):
        if not self._decomposed:
            self._decompose()
        return self._desc

    def type(self):
        if not self._decomposed:
            self._decompose()
        return self._type

    def _decompose(self):
        """
        _decompose parses self._name into individual components.
        """
        # Record that name has been decomposed ahead of time
        self._decomposed = True

        name = self._name
        starts = name.split("_", 3)
        if len(starts) == 4:
            # Fast path
            self._side     = starts[0]
            self._module   = starts[1]
            self._basename = starts[2]
            desc, _, _type = starts[3].rpartition("_")
            if desc == "":
                desc = None
            self._desc = desc
            self._type = _type
            return

        # Valid components are missing; decompose on a best effort basis
        # based on the records of valid values for side, module, and type.

        # side
        if starts[0].upper() in SBConvention.sides:
            self._side = starts[0]
            if len(starts) == 1:
                return
            starts = starts[1:]

        # module
        if starts[0].lower() in SBConvention.modules:
            self._module = starts[0]
            if len(starts) == 1:
                return
            starts = starts[1:]

        # type
        if starts[-1].upper() in SBConvention.types:
            self._type = starts[-1]
            if len(starts) == 1:
                return
            starts = starts[:-1]

        # basename and description components are pure guesses
        self._basename = starts[0]
        self._desc = "_".join(starts[1:])

    #########################################
    # IMPLEMENTATIONS OF BASE CLASS METHODS #
    #########################################

    def name(self):
        if self._name is None:  # build name from components
            components = []
            if self._side is not None:
                components.append(self._side)
            if self._module is not None:
                components.append(self._module)
            if self._basename is not None:
                components.append(self._basename)
            if self._desc is not None:
                components.append(self._desc)
            if self._type is not None:
                components.append(self._type)
            self._name = "_".join(components)
        return self._name

    def is_valid(self):
        if not super(SBName, self).is_valid():  # Check legal Maya name
            return False
        if self.side() not in SBConvention.sides:
            return False
        if self.module() not in SBConvention.modules:
            return False
        if self.type() not in SBConvention.types:
            return False
        bn = self.basename()
        if bn is None or "_" in bn:
            return False
        desc = self.description()
        if desc is not None:
            if len(desc) == 0:
                return False  # should be absent instead
            if desc[0] == "_" or desc[-1] == "_":
                return False  # should not start or end with underscore
        return True

    def replace(self, side=None, module=None, basename=None, desc=None, type=None, **unsupported):
        if len(unsupported) > 0:
            raise UnknownComponentError(SBConvention(), unsupported.keys())
        return SBName(
            side=(self.side() if side is None else str(side)),
            module=(self.module() if module is None else str(module)),
            basename=(self.basename() if basename is None else str(basename)),
            desc=(self.description() if desc is None else str(desc)),
            type=(self.type() if type is None else str(type)),
        )

    def get_component(self, component):
        getter = SBName._componentDispatch.get(component)
        if getter is None:
            raise UnknownComponentError(SBConvention(), component)
        return getter()

    # a table mapping component names to getter methods
    _componentDispatch = {
        "side": side,
        "module": module,
        "basename": basename,
        "desc": description,
        "type": type,
    }
