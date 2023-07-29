from pyphil.test import TestCase
from pyphil import Namespace

import maya.cmds as cmds

def _new(*args, **kwargs):
    return Namespace.__new__(Namespace, *args, **kwargs)

class TestNamespace(TestCase):

    def test_call_ns_success(self):
        ns = Namespace("ns")
        self.assertIs(Namespace(ns), ns)

    def test_call_str_success(self):
        strings = [
            "relative:name:space",
            ":absolute:name:space",
            "namespace",
            ":",
            "",
        ]

        for s in strings:
            self.assertIsInstance(Namespace(s), Namespace)

    def test_call_str_invalid(self):
        strings = [
            "grp|ns:obj",  # '|' present
            "a:",          # Empty namespace name (in a)
            "a::c",        # Empty namespace name (in a)
        ]

        for s in strings:
            with self.assertRaises(ValueError) as _:
                Namespace(s)

    def test_current(self):
        self.assertEqual(Namespace.current, Namespace.root)

        cmds.namespace(addNamespace="ns")
        cmds.namespace(setNamespace="ns")

        self.assertEqual(Namespace.current, Namespace(":ns"))

    def test_root(self):
        self.assertEqual(Namespace(":"), Namespace.root)

    def test_join_success(self):
        cases = {
            ("a", "b:c", "d"):           Namespace("a:b:c:d"),
            ("a", ":b:c", ":d"):         Namespace("a:b:c:d"),
            (":foo", "bar", ":"):        Namespace(":foo:bar"),
            (Namespace.root, "foo:bar"): Namespace(":foo:bar"),
            (":", "foo", "", "bar"):     Namespace(":foo:bar"),
            ("", "foo", ":bar"):         Namespace(":foo:bar"),
            (":",):                      Namespace.root,
            ("",):                       Namespace.root,
            (":", "", Namespace.root):   Namespace.root,
        }
        for args, expected in cases.items():
            res = Namespace.join(*args)
            self.assertEqual(expected, res)

    def test_join_invalid(self):
        cases = [
            ("a:", "b"),
            ("a::c", "d"),
            ("grp|ns",),
            (),
        ]
        for args in cases:
            with self.assertRaises(ValueError) as _:
                Namespace.join(*args)

    def test_str(self):
        cases = {
            Namespace("foo:bar:test"):              "foo:bar:test",
            Namespace.join(":foo", ":bar", "test"): ":foo:bar:test",
            Namespace.root:                         ":",
            _new(parent=Namespace("a"), name="b"):  "a:b",
            _new(parent=None, name="ns"):           "ns",
        }
        for ns, expected in cases.items():
            self.assertEqual(expected, ns.str())
            self.assertEqual(expected, str(ns))

    def test_abs(self):
        cases = {
            Namespace(":foo:bar"): Namespace(":foo:bar"),
            Namespace("foo:bar"):  Namespace(":foo:bar"),
            Namespace(":name"):    Namespace(":name"),
            Namespace("name"):     Namespace(":name"),
            Namespace(":"):        Namespace.root,
            Namespace.root:        Namespace.root,
        }
        for ns, expected in cases.items():
            self.assertEqual(expected, ns.abs())

    def test_abs_nonroot(self):
        cmds.namespace(addNamespace="ns")
        cmds.namespace(setNamespace="ns")
        cases = {
            Namespace(":foo:bar"): Namespace(":foo:bar"),
            Namespace("foo:bar"):  Namespace(":ns:foo:bar"),
            Namespace(":name"):    Namespace(":name"),
            Namespace("name"):     Namespace(":ns:name"),
            Namespace(":"):        Namespace.root,
            Namespace.root:        Namespace.root,
        }
        for ns, expected in cases.items():
            self.assertEqual(expected, ns.abs())

    def test_is_abs_rel(self):
        cases = {
            Namespace(":foo:bar"): True,
            Namespace("foo:bar"):  False,
            Namespace(":name"):    True,
            Namespace("name"):     False,
            Namespace(":"):        True,
            Namespace.root:        True,
        }
        for ns, expected in cases.items():
            self.assertEqual(expected, ns.is_abs())
            self.assertEqual(expected, not ns.is_rel())

    def test_is_root(self):
        cases = {
            Namespace(":ns"):                      False,
            Namespace("ns"):                       False,
            Namespace(":"):                        True,
            Namespace.root:                        True,
            _new(parent=None, name="ns"):          False,
            _new(parent=Namespace("a"), name="b"): False,
        }
        for ns, expected in cases.items():
            self.assertEqual(expected, ns.is_root())

    def test_is_valid(self):
        cases = {
            Namespace(":foo:bar"):            True,
            Namespace("F00:b_r"):             True,
            Namespace(":foo:BAR:M1X3d__42f"): True,
            Namespace(":"):                   True,
            Namespace.root:                   True,

            Namespace(" "):                   False,
            Namespace("42"):                  False,
            Namespace("_bad"):                False,
            Namespace("rød"):                 False,
            Namespace("x-ray"):               False,
            Namespace("obj.attr"):            False,
        }
        for ns, expected in cases.items():
            self.assertEqual(expected, ns.is_valid())

    def test_name(self):
        cases = {
            Namespace(":name"):           "name",
            Namespace("parent:ns"):       "ns",
            Namespace("grand:parent:ns"): "ns",
            Namespace.root:               "",
        }
        for ns, expected in cases.items():
            self.assertEqual(expected, ns.name)

    def test_parent(self):
        cases = {
            Namespace("foo:bar:dummy"): Namespace("foo:bar"),
            Namespace("foo"):           None,
            Namespace(":foo"):          Namespace.root,
            Namespace.root:             None,
        }
        for ns, expected in cases.items():
            self.assertEqual(expected, ns.parent)

    def test_depth(self):
        cases = {
            Namespace(":foo:bar"): 2,
            Namespace("foo:bar"):  1,
            Namespace(":foo"):     1,
            Namespace("foo"):      0,
            Namespace.root:        0,
        }
        for ns, expected in cases.items():
            self.assertEqual(expected, ns.depth)

    def test_hierarchy(self):
        cases = {
            Namespace(":a:sample:namespace"): [
                Namespace.root,
                Namespace(":a"),
                Namespace(":a:sample"),
                Namespace(":a:sample:namespace"),
            ],
            Namespace.root: [Namespace.root],
        }
        for ns, expected in cases.items():
            self.assertEqual(expected, ns.hierarchy())

    def test_hierarchy_copied(self):
        ns = Namespace(":ns")
        ns.hierarchy()[0] = Namespace("mutation")
        self.assertEqual(ns.hierarchy(), [Namespace.root, ns])

    def test_split(self):
        cases = {
            Namespace(":a:b:c"): (Namespace(":a:b"), Namespace("c")),
            Namespace("a:b:c"):  (Namespace("a:b"),  Namespace("c")),
            Namespace(":name"):  (Namespace.root,    Namespace("name")),
            Namespace("name"):   (None,              Namespace("name")),
            Namespace.root:      (None,              Namespace.root),
        }
        for ns, expected in cases.items():
            self.assertEqual(expected, ns.split())

    def test_split_root(self):
        cases = {
            Namespace(":a:b:c"): (Namespace.root,    Namespace("a:b:c")),
            Namespace("a:b:c"):  (Namespace("a"),    Namespace("b:c")),
            Namespace(":name"):  (Namespace.root,    Namespace("name")),
            Namespace("name"):   (Namespace("name"), None),
            Namespace.root:      (Namespace.root,    None),
        }
        for ns, expected in cases.items():
            self.assertEqual(expected, ns.split_root())

    def test_equality(self):
        cases = [
            (Namespace("foo:bar:test"),              Namespace("foo:bar:test")),
            (Namespace.root,                         Namespace("")),
            (_new(parent=Namespace("a"), name="b"),  Namespace("a:b")),
            (_new(parent=None, name="ns"),           Namespace("ns")),
        ]
        for a, b in cases:
            self.assertFalse(a < b)
            self.assertLessEqual(a, b)
            self.assertEqual(a, b)
            self.assertGreaterEqual(a, b)
            self.assertFalse(a > b)
            self.assertEqual(a.__cmp__(b), 0)

            self.assertEqual(hash(a), hash(b))

            self.assertFalse(b < a)
            self.assertLessEqual(b, a)
            self.assertEqual(b, a)
            self.assertGreaterEqual(b, a)
            self.assertFalse(b > a)
            self.assertEqual(b.__cmp__(a), 0)

    def test_ordered(self):
        cases = [
            (Namespace("a"),     Namespace("b")),
            (Namespace("a"),     Namespace("ab")),
            (Namespace("aa"),    Namespace("ab")),
            (Namespace("A"),     Namespace("a")),
            (Namespace("a0"),    Namespace("aA")),
            (Namespace("a:a"),   Namespace("a:b")),
            (Namespace("a:a:b"), Namespace("a:b")),
            (Namespace(":name"), Namespace("name")),
            (Namespace("a:b:c"), Namespace("a:b:c:d")),
        ]
        for a, b in cases:
            self.assertLess(a, b)
            self.assertLessEqual(a, b)
            self.assertNotEqual(a, b)
            self.assertFalse(a >= b)
            self.assertFalse(a > b)
            self.assertEqual(a.__cmp__(b), -1)

            self.assertFalse(b < a)
            self.assertFalse(b <= a)
            self.assertNotEqual(b, a)
            self.assertGreaterEqual(b, a)
            self.assertGreater(b, a)
            self.assertEqual(b.__cmp__(a), 1)
