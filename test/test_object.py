from pyphil.test import TestCase
from pyphil import Object, Name
from pyphil.errors import *

import maya.OpenMaya as om
import maya.cmds as cmds

class TestObject(TestCase):

    # SETUP

    def sceneInit(self):
        unique = cmds.sphere(name="unique")
        duplicate = cmds.sphere(name="duplicate")
        group1 = cmds.group(unique, duplicate, name="group1")
        duplicate = cmds.sphere(name="duplicate")
        group2 = cmds.group(group1, duplicate, name="group2")
        cmds.sphere(name="duplicate")

    # TESTS

    def test_list_none(self):
        self.assertEqual([], Object.list(None))

    def test_list_many(self):
        many = cmds.ls()
        objects = Object.list(many)
        self.assertEqual(list, type(objects))
        self.assertEqual(len(many), len(objects))
        for obj in objects:
            self.assertIsInstance(obj, Object)

    def test_fromName_success(self):
        obj = Object.fromName("unique")
        self.assertIsInstance(obj, Object)

    def test_fromName_notFound(self):
        with self.assertRaises(NotExistError) as _:
            Object.fromName("doesNotExist")

    def test_fromName_notFound2(self):
        with self.assertRaises(NotExistError) as _:
            Object.fromName("|unique")  # object not located at root

    def test_fromName_duplicate(self):
        with self.assertRaises(NotUniqueError) as _:
            Object.fromName("duplicate")

    def test_fromName_duplicateWildcard(self):
        with self.assertRaises(NotUniqueError) as _:
            Object.fromName("*uplicate")

    uuid = "11111111-1111-1111-1111-111111111111"

    def test_fromUUID_success_string(self):
        self.impl_fromUUID_success(TestObject.uuid)

    def test_fromUUID_success_muuid(self):
        self.impl_fromUUID_success(om.MUuid(TestObject.uuid))

    def impl_fromUUID_success(self, uuid):
        obj = Object.fromName("unique")
        TestObject.setUUID(obj, uuid)
        obj2 = Object.fromUUID(uuid)
        self.assertIsInstance(obj2, Object)

    def test_fromUUID_notFound(self):
        with self.assertRaises(NotExistError) as _:
            Object.fromUUID(TestObject.uuid)

    def test_world(self):
        obj = Object.fromName("|duplicate")
        world = obj.parent()
        self.assertEqual(world, Object.world())

    def test_eq(self):
        a = Object.fromName("unique")
        b = Object.fromName("|duplicate")
        c = Object.fromName("group1|duplicate")
        d = Object(om.MObject())

        self.assertTrue(a == a)
        self.assertTrue(b == b)
        self.assertTrue(c == c)
        self.assertTrue(d == d)

        self.assertFalse(a == b)
        self.assertFalse(b == c)
        self.assertFalse(c == d)

        self.assertFalse(a == "unique")
        self.assertFalse(b == "|duplicate")

    def test_neq(self):
        a = Object.fromName("unique")
        b = Object.fromName("|duplicate")
        c = Object.fromName("group1|duplicate")
        d = Object(om.MObject())

        self.assertFalse(a != a)
        self.assertFalse(b != b)
        self.assertFalse(c != c)
        self.assertFalse(d != d)

        self.assertTrue(a != b)
        self.assertTrue(b != c)
        self.assertTrue(c != d)

        self.assertTrue(a != "unique")
        self.assertTrue(b != "|duplicate")

    def test_bool(self):
        a = Object.fromName("unique")
        self.assertTrue(a)
        b = Object(om.MObject())
        self.assertFalse(b)

    def test_hash(self):
        a = Object.fromName("unique")
        b = Object.fromName("unique")
        self.assertEqual(1, len({a, b}), "hash function not working")

    def test_name_name(self):
        # DAG nodes
        self.assertEqual("|group2|group1|unique",    str(Object.fromName("unique").name()))
        self.assertEqual("|group2|group1|unique",    str(Object.fromName(":unique").name()))
        self.assertEqual("|duplicate",               str(Object.fromName("|duplicate").name()))
        self.assertEqual("|group2|group1|duplicate", str(Object.fromName("*1|duplicate").name()))
        self.assertEqual("|group2|group1",           str(Object.fromName("|group2|group1").name()))
        # Invalid Object
        self.assertIsNone(Object(om.MObject()).name())
        # Non-DAG nodes
        self.assertEqual("lambert1", str(Object.fromName("lambert1").name()))
        self.assertEqual("lambert1", str(Object.fromName(":lambert1").name()))
        # World node
        self.assertEqual(Name.world, Object.world().name())

    def test_name_string(self):
        # DAG nodes
        self.assertEqual("unique",           Object.fromName("unique").name(string=True))
        self.assertEqual("unique",           Object.fromName(":unique").name(string=True))
        self.assertEqual("|duplicate",       Object.fromName("|duplicate").name(string=True))
        self.assertEqual("group1|duplicate", Object.fromName("*1|duplicate").name(string=True))
        self.assertEqual("group1",           Object.fromName("|group2|group1").name(string=True))
        # Invalid Object
        self.assertIsNone(Object(om.MObject()).name(string=True))
        # Non-DAG nodes
        self.assertEqual("lambert1", Object.fromName("lambert1").name(string=True))
        self.assertEqual("lambert1", Object.fromName(":lambert1").name(string=True))
        # World node
        self.assertEqual("<world>", Object.world().name(string=True))

    def test_uuid(self):
        obj = Object.fromName("unique")
        uuid = TestObject.getUUID(obj)
        self.assertEqual(uuid.asString(), obj.uuid())

    def test_parent_group(self):
        unique = Object.fromName("unique")
        parent = unique.parent()
        self.assertIsNotNone(parent)
        self.assertEqual("|group2|group1", str(parent.name()))

    def test_parent_world(self):
        group2 = Object.fromName("|group2")
        parent = group2.parent()
        self.assertEqual(Object.world(), parent)

    def test_parent_none_world(self):
        group2 = Object.fromName("|group2")
        world = group2.parent()
        self.assertIsNone(world.parent())

    def test_parent_none_nonDag(self):
        nonDAG = Object.fromName("lambert1")
        parent = nonDAG.parent()
        self.assertIsNone(parent)

    # HELPERS

    @classmethod
    def getUUID(cls, obj):
        return obj._node.uuid()

    @classmethod
    def setUUID(cls, obj, uuid):
        if isinstance(uuid, str):
            uuid = om.MUuid(uuid)
        obj._node.setUuid(uuid)


