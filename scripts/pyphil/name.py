import copy

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

# The different degrees to which a Name can be decomposed
_unsplit     = 0
_parentSplit = 1
_nsSplit     = 2

class Name(object):
    """
    Name represents an immutable Maya name or DAG path.
    """

    # world = Object.world().name().
    world = None  # Initialized after the Name class definition

    @classmethod
    def of(cls, name):
        """
        of returns a Name representing the given name, which must be a string,
        a NameComposition, or an existing Name object.

        :param name: The name to return a Name for.
        :returns:    a Name object.
        """
        if isinstance(name, Name):
            return name
        if isinstance(name, NameComposition):
            return Name(state=_nsSplit, base=name)
        if not isinstance(name, basestring):
            raise ValueError("cannot create Name from non-string type (was type: {:s})".format(name.__class__))
        return Name(name)

    @classmethod
    def build(cls, parent=None, short=None, namespace=None, base=None, nc=None, **components):
        """
        build constructs a Name object from the given arguments.

        Any arguments beyond parent, short, namespace, base, and nc are
        interpreted as naming convention components. If nc is passed, that
        argument is assumed to be a NamingConvention that can be used to
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
                           parent of the returned Name.
        :param short:      A string or Name representing the name of the
                           object, potentially including a namespace and/or
                           DAG node parents.
        :param namespace:  A string or Namespace representing the namespace
                           part of the object name.
        :param base:       A string containing the name itself with no parents
                           or namespaces. A NameComposition created by a
                           NamingConvention may also be passed.
        :param nc:         A PyPhil NamingConvention to use for composing a
                           base name from other given naming convention
                           components. If None and neither short nor base
                           arguments are given then nc will be set to the
                           result of NamingConvention.get().
        :param components: Naming convention components that nc.compose() can
                           be called with to produce a base name, if both the
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
            if isinstance(base, basestring):
                if "|" in base:
                    raise ValueError("invalid 'base' argument; path separator '|' found in '{:s}'".format(base))
            elif not isinstance(base, NameComposition):
                raise ValueError("invalid 'base' argument; only string or NameComposition allowed (was type: {:s})".format(base.__class__))
        elif len(components) > 0:
            # Construct base from components
            if nc is None:
                nc = NamingConvention.get()
            base = nc.compose(**components)
        else:
            raise ValueError("failed to construct Name: either 'short', 'base', or name components must be passed")

        # Construct name
        if parent is not None:
            parent = Name.of(parent)
        if namespace is not None:
            namespace = Namespace.of(namespace)
        return Name(state=_nsSplit, parent=parent, namespace=namespace, base=base)

    @classmethod
    def join(cls, *names):
        """
        join creates a DAG path from multiple parts. Each part may be a string,
        a Name, or a NameComposition. The result is all parts concatenated from
        left to right, separated by exactly one '|'. For example:

            join("|foo", "|bar", "_42") == Name.of("|foo|bar|_42")

        It is assumed that each part is a valid name or DAG path, either a
        relative path such as "foo" or "foo|bar" or an absolute path such as
        "|foo" or "|foo|bar".

        Special rules apply for parts that are "<world>", the empty string, or
        Name or NameComposition objects representing either. Either four is
        referred to just as <world> in the following.
        If the first of multiple parts is <world>, then the constructed Name
        will be an absolute path. Likewise if <world> is the only part then
        Name.world is returned. If <world> is any but the first part then that
        part is ignored.

        Examples:
            join("<world>", "foo", "<world>", "bar") == Name.of("|foo|bar")
            join(Name.world, "foo")                  == Name.of("|foo")
            join("", "bar", "")                      == Name.of("|bar")
            join("<world>")                          == Name.world
            join("")                                 == Name.world
            join("<world>", Name.world, "")          == Name.world

        :param names: list of DAG path names to join
        :return:      A Name object representing the combined path.
        """
        n = len(names)
        if n == 0:
            return None
        if n == 1:
            return Name.of(names[0])

        # last = names[-1]
        # if isinstance(last, Name):
        #     if last.hasParent():
        #
        # elif isinstance(last, NameComposition):
        #
        # elif isinstance(last, basestring):
        #
        # else:

        raise NotImplementedError  # TODO

    def __init__(self, name=None, state=_unsplit, root=None, parent=None, short=None, namespace=None, base=None):
        if name == "":
            raise ValueError("invalid name ''; empty string forbidden")
        self._name      = name       # The full name (string); may be None if only component are provided
        self._state     = state      # The degree to which name or short has been decomposed (int)
        self._root      = root       # The top parent in the path (Name); None until computed
        self._parent    = parent     # The parent of this name (Name); None until computed
        self._short     = short      # <namespace>:<base> if <namespace> is not None (string); None until computed
        self._namespace = namespace  # Non-root namespace component of short (Namespace); None until computed
        self._base      = base       # Short name without namespace component (string); None until computed

    def __str__(self):
        """
        :returns: self.str()
        """
        return self.str()

    def __repr__(self):
        return 'Name("{:s}")'.format(self.str())

    def str(self):
        """
        str returns the name represented by Name as string.
        If Name was created from a string rather than components, the result
        will match a substring of the original string. If the original string
        contained superfluous root namespace declarations, so will the result.

        Examples:
            Name.of("|ns:foo|:bar|test").str()           == "|ns:foo|:bar|test"
            Name.join("|ns:foo", ":bar", "test").str()   == "|ns:foo|:bar|test"
            Name.build(namespace="",   base="bar").str() == ":bar"
            Name.build(namespace=None, base="bar").str() == "bar"

        :returns: a string representation of the name
        """
        if self._name is None:
            name   = self.short()
            parent = self.parent()
            if parent is not None:
                if parent == Name.world:
                    name = "|" + name
                else:
                    name = parent.str() + "|" + name
            self._name = name
        return self._name

    def root(self):
        """
        root returns the first part of self's DAG path as Name.
        This is the top parent of self, or self if self has no parent.

        Examples:
            Name.of("foo|bar|dummy").root() == Name.of("foo")
            Name.of("foo").root()           == Name.of("foo")
            Name.of("|foo").root()          == Name.world

        :returns: a Name for the first path component in the DAG path
        """
        if self._root is None:
            if self._state >= _parentSplit:
                p = self._parent
                self._root = self if p is None else p.root()
            else:
                # Find root without creating parents
                parts = self._name.split("|", 1)
                if len(parts) == 2:
                    r = parts[0]
                    self._root = Name.world if r == "" else Name(r)
                else:
                    self._root = self
        return self._root

    def parent(self):
        """
        parent returns a Name representing the path to the previous component
        in self's DAG path. If self has no parent, None is returned.

        Examples:
            Name.of("foo|bar|dummy").parent() == Name.of("foo|bar")
            Name.of("foo").parent()           == None
            Name.of("|foo").parent()          == Name.world

        :returns: a Name for the parent component in the DAG path
        """
        if self._state < _parentSplit:
            parts = self._name.rsplit("|", 1)
            if len(parts) == 2:
                p = parts[0]
                p = Name.world if p == "" else Name(p, root=self._root)
                self._parent = p
            self._short = parts[-1]
            self._state = _parentSplit
        return self._parent

    def hasParent(self):
        """
        hasParent returns True if self's DAG path has a parent component.

        Examples:
            Name.of("foo|bar").hasParent() == True
            Name.of("|foo").hasParent()    == True
            Name.of("foo").hasParent()     == False
            Name.world.hasParent()         == False

        :returns: True if self.parent() is not None
        """
        return self.parent() is not None

    def namespace(self, inclRoot=True):
        """
        namespace returns a Namespace representation of self's namespace.
        If no explicit namespace has been declared this will be Namespace.root.

        If the inclRoot parameter has been set to False then namespace will
        return None if it otherwise would have returned Namespace.root

        Examples:
            Name.of("ns:grp|foo:bar").namespace() == Namespace.of("foo")
            Name.of("a:b:c:foo:bar").namespace()  == Namespace.of("a:b:c:foo")
            Name.of("ns:grp|bar").namespace()     == Namespace.root
            Name.of(":bar").namespace()           == Namespace.root
            Name.of("bar").namespace()            == Namespace.root

            Name.of(":bar").namespace(inclRoot=False) == None
            Name.of("bar").namespace(inclRoot=False)  == None


        :param inclRoot: if False, namespace will return None if self's name
                         resides in the root namespace.

        :returns:        a Namespace representation of self's namespace.
        """
        if self.hasNamespace():
            ns = self._namespace
            if not inclRoot and ns == Namespace.root:
                ns = None
            return ns
        elif inclRoot:
            return Namespace.root
        else:
            return None

    def hasNamespace(self):
        """
        hasNamespace returns True if the represented name explicitly declares
        a namespace. Note that all names that does not declare a namespace use
        the root namespace.

        Examples:
            Name.of("ns:grp|foo:bar").hasNamespace() == True
            Name.of("a:b:c:foo:bar").hasNamespace()  == True
            Name.of("ns:grp|bar").hasNamespace()     == False
            Name.of(":bar").hasNamespace()           == True
            Name.of("bar").hasNamespace()            == False

        :returns: True if self's name explicitly declares a namespace
        """
        if self._state < _nsSplit:
            self.parent()  # ensure _state == _parentSplit
            parts = self._short.rsplit(":", 1)
            if len(parts) == 2:
                self._namespace = Namespace.of(parts[0])
            self._base = parts[-1]
            self._state = _nsSplit
        return self._namespace is not None

    def base(self):
        """
        base returns as string the represented name, without parents or namespaces.

        Examples:
            Name.of("|name").base()          == "name"
            Name.of("ns:name").base()        == "name"
            Name.of("grp|ns:base").base()    == "base"
            Name.world.base()                == "<world>"

        :return: the base of the represented name
        """
        if self._state < _nsSplit:
            self.hasNamespace()  # also sets self._base
        return str(self._base)  # _base may be a NameComposition

    def short(self, namespace=None):  # include namespace as needed (None), always (True), never (False); use this specific (string or Namespace)
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
        elif isinstance(other, basestring):
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
