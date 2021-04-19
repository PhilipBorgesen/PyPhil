from pyphil.convention import NamingConvention, NameComposition

class Namespace(object):
    root = None

    @classmethod
    def of(cls, ns):
        if isinstance(ns, Namespace):
            return ns
        return Namespace(ns)

    @classmethod
    def join(cls, nc=None, *names):
        pass

    def __init__(self, ns):
        self._ns = ns

    def __str__(self):
        return self.str()

    def __repr__(self):
        return 'Name("{:s}")'.format(self.str())

    def str(self):
        return self._ns

    def __eq__(self, other):
        pass

    def __ne__(self, other):
        x = self == other
        if x is not NotImplemented:
            return not x
        return NotImplemented

    def name(self):
        pass

    def parent(self):
        pass

    def split(self, root=False):
        pass

    def isValid(self, name):
        pass

    def depth(self):
        pass

    def __add__(self, other):
        pass

    def __truediv__(self, other):
        pass

    def isRoot(self):
        return self._ns == ""

Namespace.root = Namespace("")

class Name(object):
    # world = Object.world().name().
    world = None  # Initialized after the Name class definition

    @classmethod
    def of(cls, name):
        """
        of returns a Name representing the given name, which must be a string
        or an existing Name object.

        :param name: The name to return a Name for.
        :returns:    a Name object.
        """
        if isinstance(name, Name):
            return name
        if not isinstance(name, str):
            raise ValueError("non-string name passed")
        return Name(name)

    @classmethod
    def build(cls, parent=None, short=None, namespace=None, base=None, nc=None, **components):
        """
        build constructs a Name object from the given arguments.

        Any arguments beyond parent, short, namespace, base, and nc are
        interpreted as naming convention components. If nc is passed, that
        argument is assumed to be a naming convention that can be used to
        compose a name from the components. If nc is None then the currently
        active naming convention will be retrieved via NamingConvention.get().

        Some arguments are mutually exclusive:

            1) If short is passed then neither namespace, base, nor naming
               convention components may be passed.

            2) If base is passed then naming convention components may not
               be passed.

        :param parent:     A string or Name representing a parent in the DAG
                           path of the returned Name. If the short argument
                           denotes no parent then this will be the direct
                           parent of the Name.
        :param short:      A string or Name representing the name of the
                           object, potentially including a namespace and/or
                           DAG node parent.
        :param namespace:  A string or Namespace representing the namespace
                           part of the object name.
        :param base:       A string containing the name itself with no parents
                           or namespaces. Non-strings will be converted to
                           string using the built-in str() function.
        :param nc:         A PyPhil NamingConvention to use for composing a
                           base name from other given naming convention
                           components. If None and neither short nor base
                           arguments are given then nc will be set to the
                           result of NamingConvention.get().
        :param components: Naming convention components that nc.compose() can
                           be called with to produce a base name if both the
                           short and base arguments are None.
        :return:           A Name object built from the given parts.
        """
        if short is not None:
            # Verify that none of short's components also are passed
            if namespace is not None:
                raise ValueError("mutually exclusive arguments 'short' and 'namespace' passed")
            if base is not None:
                raise ValueError("mutually exclusive arguments 'short' and 'base' passed")
            if len(components) > 0:
                raise ValueError("mutually exclusive arguments 'short' and name components passed")
            # Construct name
            if parent is None:
                return Name.of(short)
            return Name.join(parent, short)

        if base is not None:
            if len(components) > 0:
                raise ValueError("mutually exclusive arguments 'base' and name components passed")
            if not isinstance(base, NameComposition):
                base = str(base)
        else:
            # Construct base from components
            if nc is None:
                nc = NamingConvention.get()
            base = nc.compose(**components)

        # Construct name
        if parent is not None:
            parent = Name.of(parent)
        if namespace is not None:
            namespace = Namespace.of(namespace)
        return Name(parent=parent, namespace=namespace, base=base)

    @classmethod
    def join(cls, *names):
        pass

    @classmethod
    def common(cls, *names):
        pass

    def __init__(self, name=None, parent=None, namespace=None, base=None):
        if name == "":
            raise ValueError("invalid name ''; empty string forbidden")
        self._name = name

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

    def hasParent(self):
        pass

    def namespace(self):
        pass

    def hasNamespace(self):
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
    # Use dynamic attributes to read components via naming convention

    def depth(self):
        pass

    def split(self, root=False):
        pass

    def isValid(self, name):
        pass

    def isFull(self):
        """
        isFull returns True if self denotes a full path incl. leading '|' or
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
