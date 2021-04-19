from pyphil.errors import UnknownComponentError
from pyphil.convention.core import NamingConvention, NameComposition

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
    and the digits 0-9. Underscores are NOT permitted.

    <desc> is optional. When present it consists of one or more letters a-z,
    A-Z, underscores, and the digits 0-9. It may not start nor end with
    underscore.

    When a component is missing, the trailing underscore should also be
    absent. When fewer than four components (the minimum for a valid name)
    are present, SBConvention will attempt to label each the best it can
    based on the possible values for <side>, <module>, and <type>.

    NOTE: This class definition is shadowed by a variable declaration.
          The variable "SBConvention" refers to an object of this class.
    """

    # TODO: Complete these sets.
    # Sets of known values for the <side>, <module> and <type> components.
    # A name using a side, module, or type that is not in these sets will not
    # be considered valid. The more complete these sets are, the better
    # SBConvention is at splitting improper names into their true components.
    #
    # <side> and <module> names MAY NOT contain underscores.
    # <type> names MAY contain underscores.
    sides   = {"R", "L", "C", "T", "B"}
    modules = {"arm", "leg", "spine", "neck", "head", "tail", "hand", "foot"}
    types   = {"bls", "ctrl", "FK_ctrl", "fol", "geo", "Grp", "IK_ctrl", "jnt", "msh", "loc", "pin", "srf"}

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
            raise UnknownComponentError(SBConvention, unsupported.keys())
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
        return SBName(None, str(side), str(module), str(basename), desc, str(type))

# Shadow the class definition with an instance of it, thereby creating a singleton.
SBConvention = SBConvention()

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

    # These getters implement lazy parsing of the name.
    # Names are not split into components before they are needed.

    def side(self):
        """
        :return: <side> component or None if missing
        """
        if not self._decomposed:
            self._decompose()
        return self._side

    def module(self):
        """
        :return: <module> component or None if missing
        """
        if not self._decomposed:
            self._decompose()
        return self._module

    def basename(self):
        """
        :return: <basename> component or None if missing
        """
        if not self._decomposed:
            self._decompose()
        return self._basename

    def description(self):
        """
        :return: <desc> component or None if not set
        """
        if not self._decomposed:
            self._decompose()
        return self._desc

    def type(self):
        """
        :return: <type> component or None if missing
        """
        if not self._decomposed:
            self._decompose()
        return self._type

    # Generate lowercase versions of the fixed component sets
    # such that they can be used to aid decomposition.
    _sides     = {s.lower() for s in SBConvention.sides}
    _modules   = {m.lower() for m in SBConvention.modules}
    _types     = {t.lower() for t in SBConvention.types}
    # _hardTypes contain all <type> values that contain underscores,
    # longest values first. Parsing will select the longest valid match.
    _hardTypes = [t for t in _types if "_" in t]
    _hardTypes.sort(key=lambda t: len(t), reverse=True)  # sort by length

    def _decompose(self):
        """
        _decompose parses self._name into individual components.
        """
        # Record ahead of time that name has been decomposed
        self._decomposed = True

        name = self._name  # for ease of reference

        # Split out any <type> component containing underscore(s).
        # The match is greedy, so we take the longest suffix that
        # match a known value.
        small = name.lower()
        for t in SBName._hardTypes:
            if small.endswith(t):
                if len(name) == len(t):
                    self._type = name  # name is only <type>
                    return
                before = -len(t)-1
                if name[before] == "_":
                    name, semi, self._type = name[:before], "_", name[before+1:]
                    break
        else:  # split out what is expectedly the <type>
            name, semi, self._type = name.rpartition("_")

        starts = name.split("_", 3)
        if len(starts) >= 3:  # Fast path, the most common
            self._side     = starts[0]
            self._module   = starts[1]
            self._basename = starts[2]
            if len(starts) == 4:
                self._desc = starts[3]
            return

        # Valid components are missing; decompose on a best effort basis
        # based on the records of valid values for side, module, and type.

        if semi == "":  # the only component is currently assigned to <type>
            starts = []

        # Undo any invalid <type> selection
        if self._type.lower() in SBName._types:
            if len(starts) == 0:
                return
        else:
            starts.append(self._type)
            self._type = None

        # Verify potential <side> value
        if starts[0].lower() in SBName._sides:
            self._side = starts[0]
            if len(starts) == 1:
                return
            starts = starts[1:]

        # Verify potential <module> value
        if starts[0].lower() in SBName._modules:
            self._module = starts[0]
            if len(starts) == 1:
                return
            starts = starts[1:]

        # basename and description components are pure guesses
        self._basename = starts[0]
        if len(starts) > 1:
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

    def isValid(self):
        if not super(SBName, self).isValid():  # Check legal Maya name
            return False
        if self.side() not in SBConvention.sides:
            return False
        if self.module() not in SBConvention.modules:
            return False
        if self.type() not in SBConvention.types:
            return False
        bn = self.basename()
        if bn is None or bn == "" or "_" in bn:
            return False
        desc = self.description()
        if desc is not None:
            if desc == "":
                return False  # should be absent instead
            if desc[0] == "_" or desc[-1] == "_":
                return False  # should not start or end with underscore
        return True

    def replace(self, side=None, module=None, basename=None, desc=None, type=None, **unsupported):
        if len(unsupported) > 0:
            raise UnknownComponentError(SBConvention, unsupported.keys())
        return SBName(
                side=(self.side()        if side     is None else str(side)),
              module=(self.module()      if module   is None else str(module)),
            basename=(self.basename()    if basename is None else str(basename)),
                desc=(self.description() if desc     is None else str(desc)),
                type=(self.type()        if type     is None else str(type)),
        )

    def getComponent(self, component):
        getter = SBName._componentDispatch.get(component)
        if getter is None:
            raise UnknownComponentError(SBConvention, component)
        return getter(self)

    # a table mapping component names to getter methods
    _componentDispatch = {
        "side":     side,
        "module":   module,
        "basename": basename,
        "desc":     description,
        "type":     type,
    }
