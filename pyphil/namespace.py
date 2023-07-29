import re
from typing import Optional, Union, Any

from .types import Placeholder, placeholder

import maya.OpenMaya as om

__all__ = ["Namespace"]

# matches a valid namespace path declaration which is any of:
#  1) The string ":".
#  2) One or more strings matching a valid namespace name, separated by
#     single colons and optionally prefixed by one. A valid namespace name
#     is a case-insensitive letter between A and Z, optionally followed by
#     case-insensitive letters between A and Z, digits, and/or underscores.
_validNS = re.compile(r"^:|:?[a-zA-Z][a-zA-Z_0-9]*(:[a-zA-Z][a-zA-Z_0-9]*)*\Z")


def _assert_validity(ns: str):
    if "|" in ns:
        raise ValueError(f"invalid namespace path '{ns}': path separator '|' found")
    if len(ns) > 1 and (ns[-1] == ":" or "::" in ns):
        raise ValueError(f"invalid namespace path '{ns}': empty names forbidden")


def _new_ns(
    ns: Union[str, Placeholder] = placeholder,
    root: Union["Namespace", Placeholder] = placeholder,
    end: Union[Optional["Namespace"], Placeholder] = placeholder,
    parent: Union[Optional["Namespace"], Placeholder] = placeholder,
    name: Union[str, Placeholder] = placeholder,
    depth: int = -1,
) -> "Namespace":
    return Namespace.__new__(Namespace, ns, root, end, parent, name, depth)


class MetaNamespace(type):

    def __call__(cls, ns: Union[str, "Namespace"]) -> "Namespace":
        """
        Returns a Namespace representing the given namespace path.

        As a special case the empty string is treated as an alias for ":",
        the path that denotes the unnamed Maya root namespace.

        Examples:
            Namespace("relative:name:space")
            Namespace(":absolute:name:space")
            Namespace("namespace")
            Namespace(":")   # == Namespace.root
            Namespace("")    # == Namespace.root

        Args:
            ns: The namespace path to return a Namespace for.

        Returns:
            A Namespace object.

        Raises:
            ValueError: If ns does not constitute a valid namespace path.
        """
        if isinstance(ns, str):
            if ns == "":
                return Namespace.root
            _assert_validity(ns)
            return _new_ns(ns)
        elif isinstance(ns, Namespace):
            return ns
        raise ValueError(f"can only create Namespace from string or Namespace types (was type: {ns.__class__})")

    @property
    def current(self) -> "Namespace":
        """
        A path to the current namespace set within the scene, by default
        Namespace.root.

        Returns:
            The current Namespace.
        """
        return _new_ns(om.MNamespace.currentNamespace(), root=Namespace.root)


class Namespace(object, metaclass=MetaNamespace):
    """
    Namespace represents an immutable Maya namespace path. Its methods provide
    utilities for forming new namespace paths or reading parts of represented
    paths.

    All methods that create a Namespace treats the empty string "" as an alias
    for ":", which denotes the unnamed Maya root namespace.

    Attributes:
        root (Namespace): The Maya unnamed root namespace given by the path ":".
    """

    root: "Namespace"  # Initialized after the Namespace class definition

    @classmethod
    def join(cls, *namespaces: Union[str, "Namespace"]) -> "Namespace":
        """
        Forms a Namespace from multiple parts.

        The result is all parts concatenated from left to right, separated by
        exactly one ':'. For example:

            Namespace.join(":foo", ":bar", "_42") == Namespace(":foo:bar:_42")

        It is assumed that each part is a valid namespace path, either a
        relative path such as "foo" or "foo:bar" or an absolute path such as
        ":foo" or ":foo:bar".

        If the first of multiple parts is ":", "", Namespace.root, or an
        absolute path then the constructed Namespace will be an absolute path;
        otherwise the constructed Namespace will be relative. If Namespace.root,
        ":", or "" appears as any but the first part then that part is ignored.

        Examples:
            Namespace.join("a", "b:c", "d")           == Namespace("a:b:c:d")
            Namespace.join("a", ":b:c", ":d")         == Namespace("a:b:c:d")
            Namespace.join(":foo", "bar", ":")        == Namespace(":foo:bar")
            Namespace.join(Namespace.root, "foo:bar") == Namespace(":foo:bar")
            Namespace.join(":", "foo", "", "bar")     == Namespace(":foo:bar")
            Namespace.join("", "foo", ":bar")         == Namespace(":foo:bar")
            Namespace.join(":")                       == Namespace.root
            Namespace.join("")                        == Namespace.root
            Namespace.join(":", "", Namespace.root)   == Namespace.root

        Args:
            *namespaces: A non-empty list of namespace paths to join.

        Returns:
            A Namespace object representing the combined namespace path.

        Raises:
            ValueError: If called with arguments of unsupported type, no
                        arguments, or arguments with illegal namespace names.
        """
        if len(namespaces) == 0:
            raise ValueError("Namespace.join must be called with at least one argument")

        ls, root = [], False
        for i, ns in enumerate(namespaces):
            if isinstance(ns, str):
                _assert_validity(ns)
                if ns == "":
                    ns = ":"
            elif isinstance(ns, Namespace):
                ns = ns.str()
            else:
                raise ValueError(f"can only join Namespace or string types (argument #{i+1} has type: {ns.__class__})")

            if ns == ":":
                if i == 0:
                    root = True
                continue
            if not ns.startswith(":"):
                ls.append(":")  # popped later if i == 0
            ls.append(ns)

        if len(ls) == 0:
            return Namespace.root

        if ls[0] == ":" and not root:
            ls.pop(0)

        return _new_ns("".join(ls))

    def __new__(
        cls,
        ns: Union[str, Placeholder] = placeholder,
        root: Union["Namespace", Placeholder] = placeholder,
        end: Union[Optional["Namespace"], Placeholder] = placeholder,
        parent: Union[Optional["Namespace"], Placeholder] = placeholder,
        name: Union[str, Placeholder] = placeholder,
        depth: int = -1,
    ) -> "Namespace":
        # Explicit definition due to MetaNamespace.__call__ shadowing.
        obj = super().__new__(cls)
        obj.__init__(ns, root, end, parent, name, depth)
        return obj

    _ns: Union[str, Placeholder]                        # The full namespace path
    _root: Union["Namespace", Placeholder]              # The first name in the namespace path
    _end: Union[Optional["Namespace"], Placeholder]     # Namespace.join(_root, _end) == self
    _parent: Union[Optional["Namespace"], Placeholder]  # The parent of this namespace path
    _name: Union[str, Placeholder]                      # The name of this namespace
    _depth: int                                         # How many parents the namespace has; negative if uncomputed

    def __init__(
        self,
        ns: Union[str, Placeholder] = placeholder,
        root: Union["Namespace", Placeholder] = placeholder,
        end: Union[Optional["Namespace"], Placeholder] = placeholder,
        parent: Union[Optional["Namespace"], Placeholder] = placeholder,
        name: Union[str, Placeholder] = placeholder,
        depth: int = -1,
    ):
        self._ns = ns           # Must be set if parent and/or name is placeholder.
        self._root = root
        self._end = end
        self._parent = parent   # Must be set if ns == placeholder
        self._name = name       # Must be set if ns == placeholder
        self._depth = depth

    def __str__(self) -> str:
        """
        The namespace path as a string.

        Returns:
            self.str()
        """
        return self.str()

    def __repr__(self) -> str:
        return f'Namespace("{self.str()}")'

    def str(self) -> str:
        """
        The namespace path as a string.

        Examples:
            Namespace("foo:bar:test").str()               == "foo:bar:test"
            Namespace.join(":foo", ":bar", "test").str()  == ":foo:bar:test"
            Namespace.root.str()                          == ":"

        Returns:
            A string representation of the namespace path.
        """
        if self._ns is placeholder:  # implies parent and name are set
            ns: str = self._name
            parent: Optional[Namespace] = self._parent
            if parent is not None:
                if self._parent.is_root():
                    p = ""
                else:
                    p = parent.str()
                ns = f"{p}:{ns}"
            self._ns = ns
        return self._ns

    def abs(self) -> "Namespace":
        """
        Translates the path to an absolute path if not already one.

        If it needs translation, the result equals:

            Namespace.join(Namespace.current, self)

        Examples (assuming Namespace.current == Namespace.root):
            Namespace(":foo:bar").abs() == Namespace(":foo:bar")
            Namespace("foo:bar").abs()  == Namespace(":foo:bar")
            Namespace(":name").abs()    == Namespace(":name")
            Namespace("name").abs()     == Namespace(":name")
            Namespace(":").abs()        == Namespace.root
            Namespace.root.abs()        == Namespace.root

        Returns:
            An absolute namespace path to the namespace identified by
            self in context of the current namespace set in the scene.
        """
        if self.is_abs():
            return self

        current, end = Namespace.current, placeholder
        if current.is_root():
            current, end = "", self

        return _new_ns(
            ns=f"{current}:{self}",
            name=self._name,
            root=Namespace.root,
            end=end,
        )

    # def exists(self) -> bool:
    #     """
    #     Does the namespace represented by this namespace path exist?
    #
    #     Example:
    #         Namespace.current = Namespace.root
    #
    #         Namespace("ns").exists()  == False
    #         Namespace(":ns").exists() == False
    #
    #         Namespace.create(":ns")
    #
    #         Namespace("ns").exists()  == True
    #         Namespace(":ns").exists() == True
    #
    #         Namespace.current = Namespace(":ns")
    #
    #         Namespace("ns").exists()  == False
    #         Namespace(":ns").exists() == True
    #
    #     Returns:
    #         Whether the namespace denoted by self exists.
    #     """
    #     return om.MNamespace.namespaceExists(self.str())

    # In the general case it is not possible to convert an absolute namespace
    # path to an equivalent relative path. This is because namespace paths
    # cannot refer to parent namespaces like file paths can with "..".
    # Conversion is thus only possible if the absolute path identifies a
    # namespace that strictly is nested within the current namespace. For this
    # reason a general-purpose "rel" method is not provided.
    #
    # Simply unrooting an absolute path from the nameless Maya root namespace
    # faces a similar problem: No relative path can exist to Namespace.root!
    # Such operation is not super useful either, as any such produced path
    # would identify the same namespace as
    #
    #    Namespace.join(Namespace.current, abs_path)
    #
    # would.
    #
    # Not providing means to convert absolute paths to relative paths also
    # serves to discourage use of relative paths. Absolute paths appears to
    # have clear advantages, such as invariance to Namespace.current changes.

    def is_abs(self) -> bool:
        """
        Is the namespace path fully specified (absolute)?

        An absolute path is a path of namespace names that starts with the
        Maya namespace root; in string form, it starts with ':'.

        An absolute path identifies the same namespace irrespective of operation
        or whether Maya is in "relative name lookup" mode or not.

        Examples:
            Namespace(":foo:bar").is_abs() == True
            Namespace("foo:bar").is_abs()  == False
            Namespace(":name").is_abs()    == True
            Namespace("name").is_abs()     == False
            Namespace(":").is_abs()        == True
            Namespace.root.is_abs()        == True

        Returns:
            True if the root of the namespace path is Namespace.root
        """
        return self.str().startswith(":")

    def is_rel(self) -> bool:
        """
        Is the namespace path only partially specified (relative)?

        A relative path is a path of namespace names that does not start with
        the Maya namespace root; in string form, it does not start with ':'.

        By default, Maya resolves a relative namespace path relative to the
        nameless Maya root namespace, i.e. as if its parent was the root.
        If "relative name lookup" is enabled however, relative namespace paths
        are resolved relative to the current namespace, whatever that has been
        set to.

        Examples:
            Namespace("foo:bar").is_rel()  == True
            Namespace(":foo:bar").is_rel() == False
            Namespace("name").is_rel()     == True
            Namespace(":name").is_rel()    == False
            Namespace(":").is_rel()        == False
            Namespace.root.is_rel()        == False

        Returns:
            not self.is_abs()
        """
        return not self.is_abs()

    def is_root(self) -> bool:
        """
        Does the namespace path represent the unnamed Maya root namespace?

        Examples:
            Namespace(":ns").is_root() == False
            Namespace("ns").is_root()  == False
            Namespace(":").is_root()   == True
            Namespace.root.is_root()   == True

        Returns:
            self == Namespace.root
        """
        return self._ns == ":"  # Always set for the Maya root namespace

    def is_valid(self) -> bool:
        """
        Is the namespace path valid according to Maya?

        A valid namespace path is one where the name of every namespace but
        Namespace.root in self.hierarchy() starts with a letter in a-z or
        A-Z, followed by any number of letters a-z, A-Z, digits 0-9, and/or
        underscores.

        Examples:
            Namespace(":foo:bar").is_valid()            == True
            Namespace("F00:b_r").is_valid()             == True
            Namespace(":foo:BAR:M1X3d__42f").is_valid() == True
            Namespace(":").is_valid()                   == True
            Namespace.root.is_valid()                   == True

            Namespace(" ").is_valid()                   == False
            Namespace("42").is_valid()                  == False
            Namespace("_bad").is_valid()                == False
            Namespace("rød").is_valid()                 == False
            Namespace("x-ray").is_valid()               == False
            Namespace("obj.attr").is_valid()            == False

        Returns:
            True if the namespace path only consists of valid names.
        """
        return _validNS.match(self.str()) is not None

    @property
    def name(self) -> str:
        """
        The name of the namespace without any qualifying parent.

        Examples:
            Namespace(":name").name           == "name"
            Namespace("parent:ns").name       == "ns"
            Namespace("grand:parent:ns").name == "ns"
            Namespace.root.name               == ""

        Returns:
            The name of the namespace.
        """
        if self._name is placeholder:
            _ = self.parent  # also sets self._name
        return self._name

    @property
    def parent(self) -> Optional["Namespace"]:
        """
        The parent of the namespace path.

        If the path has no declared parent, None is returned.

        Examples:
            Namespace("foo:bar:dummy").parent == Namespace("foo:bar")
            Namespace("foo").parent           == None
            Namespace(":foo").parent          == Namespace.root
            Namespace.root.parent             == None

        Returns:
            A Namespace for the declared parent namespace path of self.
        """
        if self._parent is placeholder:
            parts = self._ns.rsplit(":", 1)
            if len(parts) == 2:
                p = parts[0]
                if p == "":
                    p = Namespace.root
                else:
                    p = _new_ns(ns=p, root=self._root, depth=self._depth-1)
                self._parent = p
            else:
                self._parent = None
            self._name = parts[-1]
        return self._parent

    @property
    def depth(self) -> int:
        """
        How many layers of namespaces the namespace name is nested within.

        This is equivalent to the number of (in)direct parents, or
        len(self.hierarchy())-1.

        Examples:
            Namespace(":foo:bar").depth == 2
            Namespace("foo:bar").depth  == 1
            Namespace(":foo").depth     == 1
            Namespace("foo").depth      == 0
            Namespace.root.depth        == 0

        Returns:
            How deeply the namespace name is nested.
        """
        if self._depth < 0:
            if self._ns is not placeholder:
                self._depth = self._ns.count(":")
            else:
                p = self._parent
                self._depth = p.depth + 1 if isinstance(p, Namespace) else 0
        return self._depth

    def hierarchy(self) -> list["Namespace"]:
        """
        Returns a list of the namespace path and all its iteratively declared
        parents, from its root to itself.

        Examples:
            namespaces = Namespace(":a:sample:namespace").hierarchy()
            len(namespaces) == 4
            namespaces[0]   == Namespace.root
            namespaces[1]   == Namespace(":a")
            namespaces[2]   == Namespace(":a:sample")
            namespaces[3]   == Namespace(":a:sample:namespace")

        Returns:
            All subpaths of the namespace path that share the same root.
        """
        p = self.parent
        if p is not None:
            ls = p.hierarchy()
        else:
            ls = []
        ls.append(self)
        return ls

    def split(self) -> tuple[Optional["Namespace"], "Namespace"]:
        """
        Splits the namespace path into its parent and a namespace name.

        In other words:

            self.split() == ( self.parent , Namespace(self.name) )

        Examples:
            Namespace(":a:b:c").split() == (Namespace(":a:b"), Namespace("c"))
            Namespace("a:b:c").split()  == (Namespace("a:b"),  Namespace("c"))
            Namespace(":name").split()  == (Namespace.root,    Namespace("name"))
            Namespace("name").split()   == (None,              Namespace("name"))
            Namespace.root.split()      == (None,              Namespace.root)

        Returns:
            A tuple of self.parent and Namespace(self.name).
        """
        p = self.parent
        if p is None:
            end = self
        else:
            end = _new_ns(ns=self._name, end=None, parent=None, name=self._name, depth=0)
            end._root = end
        return p, end

    def split_root(self) -> tuple["Namespace", Optional["Namespace"]]:
        """
        Splits the namespace path into its root and possibly a path relative
        to that.

        Examples:
            Namespace(":a:b:c").split_root() == (Namespace.root,    Namespace("a:b:c"))
            Namespace("a:b:c").split_root()  == (Namespace("a"),    Namespace("b:c"))
            Namespace(":name").split_root()  == (Namespace.root,    Namespace("name"))
            Namespace("name").split_root()   == (Namespace("name"), None)
            Namespace.root.split_root()      == (Namespace.root,    None)

        Returns:
            A tuple of two Namespace objects of which the second may be None.
        """
        if self._end is placeholder:
            parts = self.str().split(":", 1)
            if len(parts) == 2:
                if self._root is placeholder:
                    n = parts[0]
                    if n == "":
                        r = Namespace.root
                    else:
                        r = _new_ns(ns=n, end=None, parent=None, name=n, depth=0)
                        r._root = self._root
                    self._root = r
                e = parts[1]
                self._end = _new_ns(ns=e, depth=self._depth-1) if e != "" else None
            else:
                self._root = self
                self._end = None

        return self._root, self._end

    # TODO: Namespace.current = "ns"    # Requires handling undo
    # TODO: Namespace.create("ns")      # Requires handling undo
    # TODO: ns.exists()                 # Example depends on above operations

    # TODO: ns.objects()    (returns objects in ns, optionally also in child namespaces)

    # TODO: Querying parts (__contains__)
    # TODO: Replacing parts
    # TODO: Removing parts
    # TODO: Indexing into namespace parts (__getitem__)
    # TODO: Slicing namespace parts (__getitem__)
    # TODO: Number of parts (__len__)
    
    # TODO: Iteration over namespace parts (__iter__, or f() -> Iterable)
    # TODO: Lowest common ancestor (lca(*namespaces))

    # Not currently included: When in doubt, leave it out.
    # The current functionality is equivalent to f"{ns}{s}".
    # IDEA: Make it type-aware concatenation, returning same type as s.
    # Examples:
    #
    #   Namespace(":a") + Name("b:obj")  == Name(":a:b:obj")
    #   Namespace(":")  + Name(":obj")   == Name(":obj")
    #   Namespace("a")  + Namespace("b") == Namespace("a:b")
    #
    # def __add__(self, s: Any) -> str:
    #     """
    #     The concatenation of self.str() + str(s).
    #
    #     Example:
    #         Namespace("foo") + ":bar" == "foo:bar"
    #
    #     Args:
    #         s: Something string convertible to concat after the namespace path.
    #
    #     Returns:
    #         self.str() + str(s)
    #     """
    #     return self.str() + str(s)

    def __hash__(self) -> int:
        return hash(self.str())

    def __eq__(self, other) -> bool:
        if self is other:
            return True
        if isinstance(other, Namespace):
            return self.str() == other.str()
        return NotImplemented

    def __cmp__(self, other: "Namespace") -> int:
        """
        __cmp__ implements total ordering of Namespace objects.

        Two Namespace are compared from their roots and down the hierarchy they
        represent. If their roots compare equal, the next segment is compared,
        and so on. __cmp__ thus only returns 0 if self == other.

        Examples:
            Namespace("a")      <  Namespace("b")        == True
            Namespace("a")      <  Namespace("ab")       == True
            Namespace("aa")     <  Namespace("ab")       == True
            Namespace("A")      <  Namespace("a")        == True
            Namespace("a0")     <  Namespace("aA")       == True
            Namespace("a:a")    <  Namespace("a:b")      == True
            Namespace("a:a:b")  <  Namespace("a:b")      == True
            Namespace(":name")  <  Namespace("name")     == True
            Namespace("a:b:c")  <  Namespace("a:b:c:d")  == True

        Args:
            other: The object to compare self to.

        Returns:
            -1 if self < other, 0 if self == other, 1 if self > other.
        """
        A, B = self, other
        while True:
            a, A = A.split_root()
            b, B = B.split_root()
            n1, n2 = a.name, b.name
            if n1 < n2:
                return -1
            if n1 > n2:
                return 1
            if A is None:
                return -1 if B is not None else 0
            if B is None:
                return 1

    def __lt__(self, other) -> bool:
        if not isinstance(other, Namespace):
            return NotImplemented
        return self.__cmp__(other) < 0

    def __le__(self, other) -> bool:
        if not isinstance(other, Namespace):
            return NotImplemented
        return self.__cmp__(other) <= 0

    def __gt__(self, other) -> bool:
        if not isinstance(other, Namespace):
            return NotImplemented
        return self.__cmp__(other) > 0

    def __ge__(self, other) -> bool:
        if not isinstance(other, Namespace):
            return NotImplemented
        return self.__cmp__(other) >= 0


Namespace.root = _new_ns(ns=":", end=None, parent=None, name="", depth=0)
Namespace.root._root = Namespace.root
