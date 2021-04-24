from unittest import TestCase

from pyphil.errors import UnknownComponentError
from pyphil.convention.core import NamingConvention, NamingConventionScope, NameComposition
from pyphil.convention.none import NoConvention, NoComposition

class TestNoConvention(TestCase):

    def test_scope(self):
        nc = NamingConvention()
        with NamingConventionScope(nc):  # activate a dummy convention
            with NoConvention():
                self.assertIs(NoConvention, NamingConvention.get())

    def test_isNoConvention(self):
        self.assertTrue(NoConvention.isNoConvention())

    def test_decompose_string(self):
        name = "test42"
        n = NoConvention.decompose(name)
        self.assertIsInstance(n, NameComposition)
        self.assertEqual(name, n.name())

    def test_decompose_stringlike(self):
        name = 42  # str(42) == "42"
        n = NoConvention.decompose(name)
        self.assertIsInstance(n, NameComposition)
        self.assertEqual("42", n.name())

    def test_decompose_emptyString(self):
        name = ""
        with self.assertRaises(ValueError):
            NoConvention.decompose(name)

    def test_compose_none(self):
        with self.assertRaises(ValueError):
            NoConvention.compose()

    def test_compose_any(self):
        with self.assertRaises(UnknownComponentError):
            NoConvention.compose(test="unsupported")

class TestNoComposition(TestCase):

    def test_str(self):
        n = NoComposition("test")
        self.assertEqual("test", str(n))

    def test_name(self):
        n = NoComposition("test")
        self.assertEqual("test", n.name())

    def test_replace_none(self):
        n = NoComposition("test")
        r = n.replace()
        self.assertEqual(n.name(), r.name())
        self.assertIsInstance(r, NoComposition)

    def test_replace_unsupported(self):
        n = NoComposition("test")
        with self.assertRaises(UnknownComponentError) as raised:
            n.replace(test="unsupported")
        self.assertListEqual(["test"], raised.exception.components)

    def test_getComponent_unsupported(self):
        n = NoComposition("test")
        with self.assertRaises(UnknownComponentError):
            n.getComponent("anything")
