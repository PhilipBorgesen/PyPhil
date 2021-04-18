from unittest import TestCase

import pyphil
from pyphil.errors import *
import maya.OpenMaya as om

class TestErrors(TestCase):

    def test_NotExistError_string(self):
        pattern = "|*:test42"
        self.assert_ObjectError(
            NotExistError, pattern, pattern,
        )

    def test_NotExistError_uuid(self):
        uuid = om.MUuid()
        self.assert_ObjectError(
            NotExistError, uuid, uuid.asString(),
        )

    def test_NotUniqueError_string(self):
        pattern = "|*:test42"
        self.assert_ObjectError(
            NotUniqueError, pattern, pattern,
        )

    def test_NotUniqueError_uuid(self):
        uuid = om.MUuid()
        self.assert_ObjectError(
            NotUniqueError, uuid, uuid.asString(),
        )

    def assert_ObjectError(self, clazz, identifier, expectedMsg):
        error = clazz(identifier)
        self.assertIs(identifier, error.identifier)
        self.assertIn(expectedMsg, error.message)

    def test_UnknownComponentError_one(self):
        convention = pyphil.NoConvention
        component = "test"
        error = UnknownComponentError(convention, component)
        self.assert_UnknownComponentError(error, convention, [component])

    def test_UnknownComponentError_many(self):
        convention = pyphil.NoConvention
        components = ["foo", "bar", "test"]
        error = UnknownComponentError(convention, components)
        self.assert_UnknownComponentError(error, convention, components)

    def assert_UnknownComponentError(self, error, convention, components):
        self.assertIs(convention, error.convention)
        self.assertItemsEqual(components, error.components)
        for component in components:
            self.assertIn("'" + component + "'", error.message)
