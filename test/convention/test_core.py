from unittest import TestCase

from pyphil.convention.core import *
from pyphil.convention import NoConvention

class TestNamingConvention(TestCase):

    def test_get_default(self):
        default = NamingConvention.get()
        self.assertEqual(NoConvention, default)

    def test_str(self):
        instance = NamingConvention()
        self.assertEqual(str(instance), NamingConvention.__name__)

class TestNamingConventionScope(TestCase):

    def test_str(self):
        scope = NamingConventionScope(NoConvention)
        name  = str(NoConvention)
        self.assertIn(name, str(scope))

    def test_enter(self):
        nc = NamingConvention()
        with NamingConventionScope(nc):
            self.assertIs(nc, NamingConvention.get())

    def test_exit(self):
        nc = NamingConvention()
        with NamingConventionScope(nc):
            pass
        self.assertIs(NoConvention, NamingConvention.get())

    def test_nested(self):
        nc = NamingConvention()
        with NamingConventionScope(nc):
            self.assertIs(nc, NamingConvention.get())
            nc2 = NamingConvention()
            with NamingConventionScope(nc2):
                self.assertIs(nc2, NamingConvention.get())
            self.assertIs(nc, NamingConvention.get())
        self.assertIs(NoConvention, NamingConvention.get())

    def test_exception(self):
        nc = NamingConvention()
        caught = False

        try:
            with NamingConventionScope(nc):
                raise RuntimeError()
        except RuntimeError:
            caught = True

        self.assertTrue(caught)
        self.assertIs(NoConvention, NamingConvention.get())