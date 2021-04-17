
class NamingConvention:  # Incorporate modular naming convention. Use attr getters.

    _default = None

    @classmethod
    def default(cls):
        return cls._default

    @classmethod
    def set_default(cls, nc):
        cls._default = nc

    def __init__(self):
        pass

    def compose(self, **components):
        pass

    def decompose(self, name):
        pass

    def replace(self, name, **components):
        pass

    def get(self, name, component):
        pass

    def is_valid(self, name):
        pass

    # TODO: with statement support

class Name:

    # world = Object.world().name().
    world = None  # Initialized after the Name class definition

    @classmethod
    def of(cls, name, nc=None):
        return Name(name, nc)

    @classmethod
    def build(cls, nc=None, **components):
        pass

    @classmethod
    def join(cls, nc=None, *names):
        pass

    @classmethod
    def common(cls, *names):
        pass

    def __init__(self, name, nc=None):
        if name == "":
            raise ValueError("invalid name ''; empty string forbidden")
        self._name = name
        if nc is None:
            nc = NamingConvention.default()
        self._nc = nc

    def __str__(self):
        return self.str()

    def __repr__(self):
        return 'Name("{:s}")'.format(self.str())

    def str(self):
        return self._name

    def root(self):
        pass

    def parent(self):
        pass

    def has_parent(self):
        pass

    def namespace(self):
        pass

    def has_namespace(self):
        pass

    def base(self):
        pass

    def short(self, namespace=None):  # include namespace as needed (None), always (True), never (False)
        pass

    def replace(self, **components):  # replace any component
        pass

    def __add__(self, other):
        pass

    def __truediv__(self, other):
        pass

    # path components read via slice and index expressions
    # path component iteration
    # len = depth

    def depth(self):
        pass

    def split(self, root=False):
        pass

    def is_valid(self, name):
        pass

    def is_full(self):
        """
        is_full returns True if self denotes a full path incl. leading '|' or
        self denotes the world object.

        :returns: True if self denotes a full path or the world object.
        """
        return self._name[0] == "|" or self == Name.world

    def __eq__(self, other):
        # TODO: Handle empty but explicit namespaces
        if isinstance(other, Name):
            return self._name == other._name
        elif isinstance(other, str):
            return self._name == other
        else:
            raise NotImplemented

    def __ne__(self, other):
        x = self == other
        if x is not NotImplemented:
            return not x
        return NotImplemented

    def full(self):
        pass

    def long(self):
        pass

    def unique(self, short=False):
        pass

Name.world = Name.of("<world>")
