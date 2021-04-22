import re

from pyphil.convention import NamingConvention, NameComposition

_none = object()  # a special marker for when no argument is passed

class Namespace(object):
    root = None

    @classmethod
    def of(cls, ns):
        if isinstance(ns, Namespace):
            return ns
        if ns is None:
            return Namespace.root
        if not isinstance(ns, basestring):
            raise ValueError("cannot create Namespace from non-string type (was type: {:s})".format(ns.__class__))
        return Namespace(ns)

    @classmethod
    def join(cls, nc=None, *names):
        pass

    def __init__(self, ns):
        self._ns = ns

    def __str__(self):
        return self.str()

    def __repr__(self):
        return 'Namespace("{:s}")'.format(self.str())

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
        True

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
_decomposed     = 2

# matches ':' at beginning of a string or after an '|' _if_ that colon is
# followed by a substring that:
# 1) does not contain ':'
# 2) is followed by '|' or is at the end of the string
_rootNsPattern = re.compile(r"^:|(?<=\|):(?=[^|:]*(\Z|\|))")

class Name(object):
    """
    Name represents an immutable Maya name or DAG path. Its methods provide
    utilities for creating new names or reading parts of represented names.
    """

    """
    world is a PyPhil special Name assigned to the world object.
    It is the value returned by Object.world().name(), equal to
    
        Name.of("<world>")
    
    """
    world = None  # Initialized after the Name class definition

    @classmethod
    def of(cls, name):
        """
        of returns a Name representing the given name, which must be a string,
        a NameComposition, or an existing Name object.

        Examples:
            Name.of("relative|ns:path|to|:an|object")
            Name.of("|absolute:path|example")
            Name.of("just_a_name")
            Name.of("namespace:base")
            Name.of("nested:namespace:name")

        :param name: The name to return a Name for.
        :returns:    a Name object.
        """
        if isinstance(name, Name):
            return name
        if isinstance(name, NameComposition):
            return Name(state=_decomposed, namespace=Namespace.root, base=name, depth=0)
        if not isinstance(name, basestring):
            raise ValueError("cannot create Name from non-string type (was type: {:s})".format(name.__class__))
        name = _rootNsPattern.sub(name, "")  # remove superfluous root namespaces
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
        if short is not None or base is not None:
            # Use a replace-based equivalent to avoid duplication of validation checks
            if short is None:
                short = _none
            if base is None:
                base = _none
            return Name().replace(parent=parent, short=short, namespace=namespace, base=base, **components)
        elif len(components) > 0:
            # Construct base from components
            if nc is None:
                nc = NamingConvention.get()
            try:
                base = nc.compose(**components)
            except ValueError as e:
                raise ValueError("failed to build Name using {:s} naming convention: {:s}".format(nc, e.message))
        else:
            raise ValueError("failed to construct Name: either 'short', 'base', or name components must be passed")

        # Construct name
        if parent is not None:
            parent = Name.of(parent)
        namespace = Namespace.of(namespace)
        return Name(state=_decomposed, parent=parent, namespace=namespace, base=base)

    @classmethod
    def join(cls, *names):
        """
        join creates a DAG path from multiple parts. Each part may be a string,
        a Name, or a NameComposition. The result is all parts concatenated from
        left to right, separated by exactly one '|'. For example:

            Name.join("|foo", "|bar", "_42") == Name.of("|foo|bar|_42")

        It is assumed that each part is a valid name or DAG path, either a
        relative path such as "foo" or "foo|bar" or an absolute path such as
        "|foo" or "|foo|bar".

        Special rules apply for parts that are "<world>", or NameComposition or
        Name objects representing that. Either three is referred to just as
        <world> in the following.
        If the first of multiple parts is <world>, then the constructed Name
        will be an absolute path. Likewise if <world> is the only part then
        Name.world is returned. If <world> is any but the first part then that
        part is ignored.

        Examples:
            Name.join("<world>", "foo", "<world>", "bar") == Name.of("|foo|bar")
            Name.join(Name.world, "foo")                  == Name.of("|foo")
            Name.join(Name.world, "bar", "<world>")       == Name.of("|bar")
            Name.join("<world>")                          == Name.world
            Name.join("<world>", Name.world)              == Name.world

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

    def __init__(self, name=None, state=_unsplit, root=None, parent=None, short=None, namespace=None, base=None, depth=-1):
        self._state     = state      # The degree to which name or short has been decomposed (int)
        self._name      = name       # The full name (string); may be None if only components are provided
        self._root      = root       # The top parent in the path (Name); None until computed
        self._parent    = parent     # The parent of this name (Name); None until computed
        self._short     = short      # <namespace>:<base> if <namespace> is not None (string); None until computed
        self._namespace = namespace  # Namespace component of short (Namespace); None until computed
        self._base      = base       # Short name without namespace component (string); None until computed
        self._depth     = depth      # How many parents the name has; negative until computed

        # Other attributes used to cache results
        self._end   = _none  # _end != _none implies _root != None

    def __str__(self):
        """
        :returns: self.str()
        """
        return self.str()

    def __repr__(self):
        return 'Name("{:s}")'.format(self.str())

    def str(self):
        """
        str returns the name represented by Name as string, without any
        superfluous root namespace declarations.

        Examples:
            Name.of("|ns:foo|:bar|test").str()           == "|ns:foo|bar|test"
            Name.join("|ns:foo", ":bar", "test").str()   == "|ns:foo|bar|test"
            Name.build(parent="|foo", base="bar").str()  == "|foo|bar"
            Name.build(parent="grp", short="ns:A").str() == "grp|ns:A"
            Name.build(parent="grp", short=":A").str()   == "grp|A"
            Name.build(namespace="ns", base="bar").str() == "ns:bar"
            Name.world.str()                             == "<world>"

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
            Name.world.root()               == Name.world

        :returns: a Name for the first path component in the DAG path
        """
        if self._root is None:
            if self._state >= _parentSplit:
                p = self._parent
                self._root = self if p is None else p.root()
            else:
                # Find root without creating parents
                self.splitRoot()  # sets self._root
        return self._root

    def parent(self):
        """
        parent returns a Name representing the path to the previous component
        in self's DAG path. If self has no parent, None is returned.

        Examples:
            Name.of("foo|bar|dummy").parent() == Name.of("foo|bar")
            Name.of("foo").parent()           == None
            Name.of("|foo").parent()          == Name.world
            Name.world.parent()               == None

        :returns: a Name for the parent component in the DAG path
        """
        if self._state < _parentSplit:
            parts = self._name.rsplit("|", 1)
            if len(parts) == 2:
                p = parts[0]
                p = Name.world if p == "" else Name(p, root=self._root, depth=self._depth-1)
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

    def depth(self):
        """
        depth returns how many parents the represented name has.

        :returns: how many parents self has
        """
        if self._depth < 0:
            if self._name is not None:
                self._depth = self._name.count("|")
            else:
                p = self._parent
                self._depth = 0 if p is None else p.depth() + 1
        return self._depth

    def namespace(self):
        """
        namespace returns a Namespace representation of self's namespace.
        If no explicit namespace has been declared this will be Namespace.root.

        Examples:
            Name.of("ns:grp|foo:bar").namespace() == Namespace.of("foo")
            Name.of("a:b:c:foo:bar").namespace()  == Namespace.of("a:b:c:foo")
            Name.of("ns:grp|bar").namespace()     == Namespace.root
            Name.of(":bar").namespace()           == Namespace.root
            Name.of("bar").namespace()            == Namespace.root
            Name.world.namespace()                == Namespace.root

        :returns:        a Namespace representation of self's namespace.
        """
        if self._state < _decomposed:
            self.parent()  # also sets self._short
            parts = self._short.rsplit(":", 1)
            if len(parts) == 2:
                self._namespace = Namespace.of(parts[0])
            else:
                self._namespace = Namespace.root
            self._base = parts[-1]
            self._state = _decomposed
        return self._namespace

    def hasNamespace(self):
        """
        hasNamespace returns True if the represented name resides in a
        namespace other than the root namespace. Names that do not declare
        an explicit namespace resides in the root namespace.

        Examples:
            Name.of("ns:grp|foo:bar").hasNamespace() == True
            Name.of("a:b:c:foo:bar").hasNamespace()  == True
            Name.of("ns:grp|bar").hasNamespace()     == False
            Name.of(":bar").hasNamespace()           == False
            Name.of("bar").hasNamespace()            == False
            Name.world.hasNamespace()                == False

        :returns: True if self's name resides in a non-root namespace
        """
        return not self.namespace().isRoot()

    def base(self):
        """
        base returns as string the represented name, without DAG path parents
        or namespaces.

        Examples:
            Name.of("|name").base()          == "name"
            Name.of("ns:name").base()        == "name"
            Name.of("grp|ns:base").base()    == "base"
            Name.world.base()                == "<world>"

        :return: the base of the represented name
        """
        if self._state < _decomposed:
            self.namespace()  # also sets self._base
        return str(self._base)  # _base may be a NameComposition

    def _baseDecomposition(self, nc=None):
        if self._state < _decomposed:
            self.namespace()  # also sets self._base

        if nc is None:
            nc = NamingConvention.get()

        self._base = nc.decompose(self._base)
        return self._base

    def short(self, namespace=None):
        """
        short returns as string the represented name, without DAG path parents
        but including namespaces. The exact behavior depends on the namespace
        parameter. If namespace is set to...

             None:  The returned string will be prefixed with "<namespace>:"
                    only if <namespace> differs from the root namespace.
                    This is the default behavior.
             True:  The returned string will be prefixed with "<namespace>:"
                    even if <namespace> is the root namespace.
             False: The returned string will be just the base name. No
                    namespace will be included. This is equal to self.base().

        Examples:
            Name.of("foo|bar").short()                      == "bar"
            Name.of("foo|:bar").short()                     == "bar"
            Name.of("foo|ns:bar").short()                   == "ns:bar"
            Name.of("foo|a:b:c:bar").short()                == "a:b:c:bar"
            Name.world.short()                              == "<world>"

            Name.of("foo|bar").short(namespace=True)        == ":bar"
            Name.of("foo|:bar").short(namespace=True)       == ":bar"
            Name.of("foo|ns:bar").short(namespace=True)     == "ns:bar"
            Name.of("foo|a:b:c:bar").short(namespace=True)  == "a:b:c:bar"
            Name.world.short(namespace=True)                == ":<world>"

            Name.of("foo|bar").short(namespace=False)       == "bar"
            Name.of("foo|:bar").short(namespace=False)      == "bar"
            Name.of("foo|ns:bar").short(namespace=False)    == "bar"
            Name.of("foo|a:b:c:bar").short(namespace=False) == "bar"
            Name.world.short(namespace=False)               == "<world>"

        :param namespace: controls when the namespace is included
        :returns:         the represented name as string, without DAG parents
        """
        if namespace is not None:
            if namespace is True:
                return self.namespace().str() + ":" + self.base()
            if namespace is False:
                return self.base()
            raise ValueError("unsupported 'namespace' argument {:s} passed to Name.short".format(namespace))

        # Fast path for the most common case
        if self._short is not None:
            return self._short

        if self._state < _parentSplit:
            # Decompose from name
            self.parent()  # also sets self._short
        else:
            # Compose from components
            ns = self.namespace()
            if ns.isRoot():
                self._short = self._base
            else:
                self._short = ns.str() + ":" + self._base

        return self._short

    def relative(self):
        """
        relative returns a Name corresponding to the longest subpath of self
        that does not have Name.world at its root. If self == Name.world
        then relative returns None.

        Examples:
            Name.of("|foo|bar").relative() == Name.of("foo|bar")
            Name.of("foo|bar").relative()  == Name.of("foo|bar")
            Name.world.relative()          == None

        :return: A Name of the longest subpath not rooted at the world.
        """
        root, subpath = self.splitRoot()
        if root == Name.world:
            return subpath
        return self

    def replace(self, parent=_none, short=_none, namespace=_none, base=_none, nc=None, **components):
        """
        replace returns a new Name with parts replaced as given by arguments.
        This works as calling Name.build except any parts not given by arguments
        will be provided by self, and any part set to None will be absent in the
        produced Name. It is invalid to set the short or base argument to None.

        See Name.build for documentation of each argument and valid combinations.

        Examples:
            n = Name.of("|foo|ns:bar")
            n.replace(parent="grp")                 == Name.of("grp|ns:bar")
            n.replace(parent=None)                  == Name.of("ns:bar")
            n.replace(short="name")                 == Name.of("|foo|name")
            n.replace(namespace=None)               == Name.of("|foo|bar")
            n.replace(namespace=Namespace.root)     == Name.of("|foo|:bar")
            n.replace(namespace="NS")               == Name.of("|foo|NS:bar")
            n.replace(namespace=Namespace.of("NS")) == Name.of("|foo|NS:bar")
            n.replace(base="NAME")                  == Name.of("|foo|ns:NAME")
            n.replace(namespace="NS", base="NAME")  == Name.of("|foo|NS:NAME")
            n.replace(parent=Name.world, base="xx") == Name.of("|ns:xx")

        Example, using SBConvention naming convention:

            import pyphil.convention.SBConvention

            n = Name.of("grp|R_arm_elbow_Grp")

            with SBConvention():
                n.replace(parent="goo", side="L")       == Name.of("goo|L_arm_elbow_Grp")
                n.replace(module="leg", basename="hip") == Name.of("grp|R_leg_hip_Grp")
                n.replace(parent=None, type="IK_ctrl")  == Name.of("R_arm_elbow_IK_ctrl")

                x = Name.of("|R_arm_elbow_GREAT_DESCRIPTION_Grp")
                x.replace(parent=n.parent(), desc=None) == Name.of("grp|R_arm_elbow_Grp")
                x.replace(description="boring")         == Name.of("|R_arm_elbow_boring_Grp")

        :returns: a copy of self with parts removed or replaced by the given
                  arguments.
        """

        if short is not _none:
            # Verify that none of short's components also are passed
            if namespace is not _none:
                raise ValueError("mutually exclusive arguments 'short' and 'namespace' passed")
            if base is not _none:
                raise ValueError("mutually exclusive arguments 'short' and 'base' passed")
            if len(components) > 0:
                raise ValueError("mutually exclusive arguments 'short' and name components passed")
            # A name with no short name (not even an empty one) is undefined
            if short is None:
                raise ValueError("argument 'short' must not be None")
            # Construct name
            parent = self.parent() if parent is _none else parent
            if parent is None:
                return Name.of(short)
            return Name.join(parent, short)

        if base is not _none:
            # Verify that none of base's components also are passed
            if len(components) > 0:
                raise ValueError("mutually exclusive arguments 'base' and name components passed")
            if base is None:
                # A name with no base name (not even an empty one) is undefined
                raise ValueError("argument 'base' must not be None")
            elif isinstance(base, basestring):
                if "|" in base:
                    raise ValueError("invalid 'base' argument; path separator '|' found in '{:s}'".format(base))
                if ":" in base:
                    raise ValueError("invalid 'base' argument; namespace separator ':' found in '{:s}'".format(base))
            elif not isinstance(base, NameComposition):
                raise ValueError(
                    "invalid 'base' argument; only string or NameComposition allowed (was type: {:s})".format(base.__class__))
        elif len(components) > 0:
            # Construct base from components
            base = self._baseDecomposition(nc=nc).replace(**components)
        elif self._base is not None:
            base = self._base  # Pass on any NameComposition already made
        else:
            base = self.base()

        # Inherit or construct the new parent
        if parent is _none:
            parent = self.parent()
            depth = self._depth
        elif parent is not None:
            parent = Name.of(parent)
            depth = -1

        # Inherit or construct the new namespace
        if namespace is _none:
            namespace = self.namespace()
        else:
            namespace = Namespace.of(namespace)

        return Name(state=_decomposed, parent=parent, namespace=namespace, base=base, depth=depth)

    def isFull(self):
        """
        isFull returns True if self is a DAG path rooted at the world object,
        that is has a string representation starting with '|'.

        Examples:
            Name.of("|name").isFull()    == True
            Name.of("name").isFull()     == False
            Name.of("|ns:name").isFull() == True
            Name.of("ns:name").isFull()  == False
            Name.world.isFull()          == False

        Name.world.isFull() returns False because Name.world isn't a DAG path.

        :returns: True if self denotes a full path rooted at the world object.
        """
        return self.str().startswith("|")

    def isValid(self, nc=None):
        """
        isValid returns True if the name represented by self is valid according
        to the NamingConvention given by nc. If nc is None the current naming
        convention as determined by NamingConvention.get() will be used.

        If no naming convention is provided or has been setup, the default
        naming convention will simply check whether a name is a legal Maya name.

        :param nc: The naming convention under which the name validity should
                   be determined. Defaults to NamingConvention.get() if None.
        :return:   True if the represented name is valid according to nc.
        """
        if self == Name.world:
            return True
        if not self.namespace().isValid():
            return False
        if not self._baseDecomposition(nc).isValid():
            return False

        p = self.parent()
        if p is None:
            return True
        return p.isValid(nc)

    def split(self):
        """
        split splits the DAG path represented by self into a parent and name,
        returning both as a tuple of Name objects. In other words

            self.split() == ( self.parent() , Name.of(self.short()) )

        although the computation is more effective than that.

        Examples:
            Name.of("|a|b|c").split() == (Name.of("|a|b"), Name.of("c")   )
            Name.of("a|b|c" ).split() == (Name.of("a|b"),  Name.of("c")   )
            Name.of("|name" ).split() == (Name.world,      Name.of("name"))
            Name.of("name"  ).split() == (None,            Name.of("name"))
            Name.world.split()        == (None,            Name.world     )

        :returns: A tuple of two Name objects of which the first may be None.
        """
        p   = self.parent()
        end = Name(state=self._state, short=self._short, namespace=self._namespace, base=self._base, depth=0)
        return p, end

    def splitRoot(self):
        """
        splitRoot splits the DAG path represented by self into its root and a
        subpath, returning both as a tuple of Name objects. The first Name
        is equivalent to self.root() while the second is the Name X that makes

            Name.join(self.root(), X) == self

        become True.

        Examples:
            Name.of("|a|b|c").splitRoot() == (Name.world,      Name.of("a|b|c"))
            Name.of("a|b|c" ).splitRoot() == (Name.of("a"),    Name.of("b|c")  )
            Name.of("|name" ).splitRoot() == (Name.world,      Name.of("name") )
            Name.of("name"  ).splitRoot() == (Name.of("name"), None            )
            Name.world.splitRoot()        == (Name.world,      None            )

        :return: A tuple of two Name objects of which the second may be None.
        """
        if self._end is _none:
            parts = self.str().split("|", 1)
            if len(parts) == 2:
                if self._root is None:
                    r = parts[0]
                    self._root = Name.world if r == "" else Name(r, depth=0)
                self._end = Name(parts[1], depth=self._depth-1)
            else:
                self._root = self
                self._end = None

        return self._root, self._end

    def paths(self):
        """
        paths returns a list of all self's subpaths starting at self.root().

        Example:

            paths = Name.of("|a|ns:sample|path").paths()
            len(paths) == 4
            paths[0]   == Name.world
            paths[1]   == Name.of("|a")
            paths[2]   == Name.of("|a|ns:sample")
            paths[3]   == Name.of("|a|ns:sample|path")

        :returns: a list of all subpaths starting at self.root()
        """
        p = self.parent()
        if p is not None:
            ls = p.paths()
        else:
            ls = []
        ls.append(self)
        return ls

    # TODO:
    # Use dynamic attributes to read components via naming convention

    def __add__(self, other):
        pass

    def __truediv__(self, other):
        pass

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

Name.world = Name.of("<world>")
