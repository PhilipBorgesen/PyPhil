# coding=utf-8
from unittest import TestCase

from pyphil.convention.core import *
from pyphil.convention import NoConvention
import pyphil.test

import maya.cmds as cmds

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

class TestNameComposition(pyphil.test.TestCase):

    def isMayaValid(self, name):
        if "?" in name or "*" in name:
            return False  # contains a wilcard
        try:
            sphere = cmds.sphere(name=name)[0]
            cmds.delete(sphere)
            if sphere == name:
                return True
        except TypeError:  # Object X is invalid
            return False
        except ValueError:  # No object matches name X
            return False
        return False
    
    def test_isValid_valid_start_letters(self):
        chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_"
        for c in chars:
            self.assertTrue(Name(c).isValid())
            self.assertTrue(self.isMayaValid(c))

    def test_isValid_invalid_start_digits(self):
        chars = "0123456789"
        for c in chars:
            self.assertFalse(Name(c).isValid())
            self.assertFalse(self.isMayaValid(c))

    def test_isValid_invalid_start_space(self):
        chars = " \t\n"
        for c in chars:
            self.assertFalse(Name(c).isValid())
            self.assertFalse(self.isMayaValid(c))

    def test_isValid_invalid_start_symbols(self):
        chars = '!"#$%&\'()*+,-./:;<=>?`[~]^@{|}'
        for c in chars:
            self.assertFalse(Name(c).isValid())
            self.assertFalse(self.isMayaValid(c))

    def test_isValid_invalid_start_multibyte_unicode(self):
        # Note: On some platforms, Maya allows names to contain single-byte
        #       characters from the extended ASCII range.
        chars = u"是ณה✪"
        for c in chars:
            self.assertFalse(Name(c).isValid())
            self.assertFalse(self.isMayaValid(c), u"for char '{0}'".format(c))

    def test_isValid_valid_subsequent_letters(self):
        chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_"
        for c in chars:
            n = "_" + c
            self.assertTrue(Name(n).isValid())
            self.assertTrue(self.isMayaValid(n))

    def test_isValid_valid_subsequent_digits(self):
        chars = "0123456789"
        for c in chars:
            n = "_" + c
            self.assertTrue(Name(n).isValid())
            self.assertTrue(self.isMayaValid(n))

    def test_isValid_invalid_subsequent_space(self):
        chars = " \t\n"
        for c in chars:
            n = "_" + c
            self.assertFalse(Name(n).isValid())
            self.assertFalse(self.isMayaValid(n))

    def test_isValid_invalid_subsequent_symbols(self):
        chars = '!"#$%&\'()*+,-./:;<=>?`[~]^@{|}'
        for c in chars:
            n = "_" + c
            self.assertFalse(Name(n).isValid())
            self.assertFalse(self.isMayaValid(n))

    def test_isValid_invalid_subsequent_multibyte_unicode(self):
        # Note: On some platforms, Maya allows names to contain single-byte
        #       characters from the extended ASCII range.
        chars = u"是ณה✪"
        for c in chars:
            n = "_" + c
            self.assertFalse(Name(n).isValid())
            self.assertFalse(self.isMayaValid(n), u"for char '{0}'".format(c))

# A simple NameComposition subclass to test isValid
class Name(NameComposition):
    def __init__(self, name):
        self._name = name
    
    def name(self):
        return self._name
