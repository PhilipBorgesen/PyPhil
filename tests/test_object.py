from typing import Union

from pyphil.test import TestCase
from pyphil import Object, NotExistError, NotUniqueError, InvalidObjectError

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

    def test_metaclass_call_success(self):
        obj = Object("unique")  # shorthand for Object.from_name(...)
        self.assertIsInstance(obj, Object)

    def test_from_name_success(self):
        obj = Object.from_name("unique")
        self.assertIsInstance(obj, Object)

    def test_from_name_world_success(self):
        obj = Object.from_name("<world>")
        self.assertIsInstance(obj, Object)
        self.assertEqual(obj, Object.world)

    def test_from_name_world_ns_success(self):
        obj = Object.from_name(":<world>")
        self.assertIsInstance(obj, Object)
        self.assertEqual(obj, Object.world)

    def test_from_name_notFound(self):
        with self.assertRaises(NotExistError) as _:
            Object.from_name("doesNotExist")

    def test_from_name_notFound2(self):
        with self.assertRaises(NotExistError) as _:
            Object.from_name("|unique")  # object not located at root

    def test_from_name_duplicate(self):
        with self.assertRaises(NotUniqueError) as _:
            Object.from_name("duplicate")

    def test_from_name_duplicateWildcard(self):
        with self.assertRaises(NotUniqueError) as _:
            Object.from_name("*uplicate")

    uuid = "11111111-1111-1111-1111-111111111111"

    def test_from_uuid_success_string(self):
        self.assert_from_uuid_success(TestObject.uuid)

    def test_from_uuid_success_muuid(self):
        self.assert_from_uuid_success(om.MUuid(TestObject.uuid))

    def assert_from_uuid_success(self, uuid):
        obj = Object.from_name("unique")
        TestObject.set_uuid(obj, uuid)
        obj2 = Object.from_uuid(uuid)
        self.assertIsInstance(obj2, Object)

    def test_from_uuid_notFound(self):
        with self.assertRaises(NotExistError) as _:
            Object.from_uuid(TestObject.uuid)

    def test_world(self):
        obj = Object.from_name("|duplicate")
        world = Object(obj._node.parent(0))
        self.assertEqual(world, Object.world)

    def test_eq(self):
        a = "unique"
        a1 = Object.from_name(a)
        a2 = Object.from_name(a)

        b = "|duplicate"
        b1 = Object.from_name(b)
        b2 = Object.from_name(b)

        c = "group1|duplicate"
        c1 = Object.from_name(c)
        c2 = Object.from_name(c)

        self.assertTrue(a1 == a2)
        self.assertTrue(b1 == b2)
        self.assertTrue(c1 == c2)

        self.assertFalse(a1 == b1)
        self.assertFalse(b1 == c1)

        self.assertFalse(a1 == "unique")
        self.assertFalse(b1 == "|duplicate")

    def test_neq(self):
        a = "unique"
        a1 = Object.from_name(a)
        a2 = Object.from_name(a)

        b = "|duplicate"
        b1 = Object.from_name(b)
        b2 = Object.from_name(b)

        c = "group1|duplicate"
        c1 = Object.from_name(c)
        c2 = Object.from_name(c)

        self.assertFalse(a1 != a2)
        self.assertFalse(b1 != b2)
        self.assertFalse(c1 != c2)

        self.assertTrue(a1 != b1)
        self.assertTrue(b1 != c1)

        self.assertTrue(a1 != "unique")
        self.assertTrue(b1 != "|duplicate")

    def test_hash(self):
        a = hash(Object.from_name("unique"))
        b = hash(Object.from_name("unique"))
        self.assertEqual(a, b)

    def test_str(self):
        obj = Object.from_name("group1|duplicate")
        self.assertEqual("|group2|group1|duplicate", str(obj))

    # def test_name_long(self):
    #     # DAG nodes
    #     self.assertEqual("|group2|group1|unique", str(Object.from_name("unique").path()))
    #     self.assertEqual("|group2|group1|unique", str(Object.from_name(":unique").path()))
    #     self.assertEqual("|duplicate", str(Object.from_name("|duplicate").path()))
    #     self.assertEqual("|group2|group1|duplicate", str(Object.from_name("*1|duplicate").path()))
    #     self.assertEqual("|group2|group1", str(Object.from_name("|group2|group1").path()))
    #     # Non-DAG nodes
    #     self.assertEqual("lambert1", str(Object.from_name("lambert1").path()))
    #     self.assertEqual("lambert1", str(Object.from_name(":lambert1").path()))
    #     # World node
    #     self.assertEqual(Path.world, Object.world.path())
    #
    # def test_name_short(self):
    #     # DAG nodes
    #     self.assertEqual("unique", Object.from_name("unique").name(string=True))
    #     self.assertEqual("unique", Object.from_name(":unique").name(string=True))
    #     self.assertEqual("|duplicate", Object.from_name("|duplicate").name(string=True))
    #     self.assertEqual("group1|duplicate", Object.from_name("*1|duplicate").name(string=True))
    #     self.assertEqual("group1", Object.from_name("|group2|group1").name(string=True))
    #     # Non-DAG nodes
    #     self.assertEqual("lambert1", Object.from_name("lambert1").name(string=True))
    #     self.assertEqual("lambert1", Object.from_name(":lambert1").name(string=True))
    #     # World node
    #     self.assertEqual("<world>", Object.world.name(string=True))

    def test_uuid(self):
        # DAG nodes
        obj = Object.from_name("unique")
        uuid = TestObject.get_uuid(obj)
        self.assertEqual(uuid.asString(), obj.uuid)

        # Non-DAG nodes
        obj = Object.from_name("lambert1")
        self.assertIsNotNone(obj.uuid)

        # World node
        self.assertIsNotNone(Object.world.uuid)

    def test_is_valid(self):
        obj = Object.from_name("unique")
        self.assertTrue(obj.is_valid())

        cmds.delete("unique")
        self.assertFalse(obj.is_valid())

        with self.assertRaises(InvalidObjectError) as _:
            _ = str(obj)

        with self.assertRaises(InvalidObjectError) as _:
            _ = repr(obj)

        with self.assertRaises(InvalidObjectError) as _:
            _ = obj.uuid

        with self.assertRaises(InvalidObjectError) as _:
            _ = hash(obj)

        with self.assertRaises(InvalidObjectError) as _:
            _ = obj == obj

        with self.assertRaises(InvalidObjectError) as _:
            _ = obj != obj

    def test_is_valid_restore(self):
        obj = Object.from_name("unique")
        h = hash(obj)

        cmds.delete("unique")
        cmds.undo()

        self.assertTrue(obj.is_valid())
        self.assertEqual(h, hash(obj))

    def test_invalid_op(self):
        a = Object.from_name("unique")
        b = Object.from_name("lambert1")
        cmds.delete("unique")

        # Verify that an object can be used as operand, even if invalid.
        _ = b == a

    # HELPERS

    @classmethod
    def get_uuid(cls, obj: Object) -> om.MUuid:
        return obj._node.uuid()

    @classmethod
    def set_uuid(cls, obj: Object, uuid: Union[str, om.MUuid]):
        if isinstance(uuid, str):
            uuid = om.MUuid(uuid)
        obj._node.setUuid(uuid)
