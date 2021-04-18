import re

class NamingConvention(object):
    """
    NamingConvention is the base class for all naming conventions. Its class
    methods manage the global naming convention that is in effect at a given
    time.

    The NamingConvention that currently is in effect can be retrieved by
    calling NamingConvention.get(). Code that use naming conventions, such as
    the methods of pyphil.Name, will call NamingConvention.get() when no naming
    convention explicitly is provided to them.

    By default no naming convention is in effect, as implemented by the
    NoConvention class. A naming convention can be registered for a specific
    block of code, a so-called scope. A scope can be declared as follows:

        sbnc = SBConvention                  # a sample naming convention
        with NamingConvention(sbnc):         # start a new scope
            nc = NamingConvention.get()
            print (nc is sbnc)               # prints "True"
            print Name.of("R_arm_GEO").side  # prints "R"
            # end of scope

        # outside a scope
        nc = NamingConvention.get()
        print (nc is NoConvention)           # prints "True"
        print Name.of("R_arm_GEO").side      # raises UnknownComponentError

    It is intended that every script using PyPhil opens a scope to run within.
    """
    _current = None  # Set to NoConvention at the end of file

    @classmethod
    def get(cls):
        """
        get returns the naming convention that currently is in effect.

        :returns: the naming convention currently in effect.
        """
        return NamingConvention._current

    @classmethod
    def __call__(cls, nc):
        """
        __call__ returns a new NamingConventionScope to be used with
        the "with" statement construct. See the class documentation
        above.

        :param nc: the naming convention to use for the new scope.
        :return:   a NamingConventionScope representing the scope.
        """
        return NamingConventionScope(nc)

    def __str__(self):
        return self.__class__.__name__

    def __repr__(self):
        return str(self)

    ###########################################
    # METHODS TO BE IMPLEMENTED BY SUBCLASSES #
    ###########################################

    def decompose(self, name):
        """
        decompose returns an instance of NameComposition that describes name
        and its components. The name parameter is a string containing the name
        of a Maya object without any namespaces or DAG path parents, or an
        object that can be converted to such string using the built-in str()
        function.

        The specific instance that is returned should be of a subclass of
        NameComposition that handles name based on the naming convention
        denoted by self.

        :param name: A Maya node name without namespaces or DAG parents.
        :return:     A NameComposition object through which the name and its
                     conventional components can be accessed.
        """
        raise NotImplementedError

    def compose(self, **components):
        """
        compose returns a NameComposition instance that describes a Maya node
        name made up by the given string components. Which components are valid
        and how they are combined is decided by the naming convention denoted
        by self.

        :param components: key-value arguments giving each component.
        :return:           A NameComposition object through which the node name
                           and its conventional components can be accessed.

        :raises UnknownComponentError: if one or more components are not
                supported by the naming convention.
        :raises ValueError: if one or more components are missing to compose a
                            valid name.
        """
        raise NotImplementedError

class NamingConventionScope(object):
    """
    A NamingConventionScope defines the boundaries of a naming convention scope.

    See https://docs.python.org/2.7/reference/compound_stmts.html#the-with-statement
    for documentation on how NamingConventionScope works with "with" statements.
    """

    def __init__(self, nc):
        self._nc = nc

    def __enter__(self):
        self._prev = NamingConvention._current
        NamingConvention._current = self._nc

    def __exit__(self, exc_type, exc_val, exc_tb):
        if NamingConvention._current != self._nc:
            # A naming convention scope must not be closed before all its inner scopes.
            raise RuntimeError("Naming convention scope attempted closed before a child scope.")

        NamingConvention._current = self._prev
        return False  # do not suppress a potential exception

class NameComposition(object):

    def __str__(self):
        """
        __str__ returns the name described by self.
        """
        return self.name()

    # Legal node names begin with any character from a-z or A-Z and an
    # underscore, followed by a sequence of characters from a-z or A-Z,
    # underscore or numerals.
    _mayaNameRegex = re.compile(r"^[a-zA-Z_][a-zA-Z_0-9]*$")

    ##########################################
    # METHODS TO BE OVERRIDDEN BY SUBCLASSES #
    ##########################################

    def is_valid(self):
        """
        is_valid returns whether the name described by self is valid according
        to the naming convention that self operates under. By default is_valid
        returns True if self.name() is a legal Maya node name.

        Legal node names begin with any character from a-z or A-Z and an
        underscore, followed by a sequence of characters from a-z or A-Z,
        underscore or numerals.

        Subclasses should override this method to validate each component as
        denoted by their naming convention.

        :returns: True if self.name() is valid according to the naming
                  convention associated with self.
        """
        return NameComposition._mayaNameRegex.match(self.name())

    def name(self):
        """
        :return: the name described by self
        """
        raise NotImplementedError

    def replace(self, **components):
        """
        replace returns a NameComposition of the same type as self with the
        same components except those given as arguments. Components listed
        by arguments will be replaced by the associated argument values.

        :param components: key-value arguments listing component replacements.
        :return:           a NameComposition describing the mutated name.

        :raises UnknownComponentError: if one or more components are not
                supported by the associated naming convention.
        """
        raise NotImplementedError

    def get_component(self, component):
        """
        get_component returns the string value of the given component name.

        :param component: name of the component to return
        :return:          the value of the given component, or None

        :raises UnknownComponentError: if the component is unsupported
                by the associated naming convention.
        """
        raise NotImplementedError

# Need to do this last since pyphil.convention.none depends on core
from pyphil.convention.none import NoConvention
NamingConvention._current = NoConvention
