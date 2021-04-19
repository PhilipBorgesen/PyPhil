from unittest import TestCase

from pyphil.errors import UnknownComponentError
from pyphil.convention.core import NamingConvention, NamingConventionScope, NameComposition
from pyphil.convention.sb import SBConvention, SBName

class TestSBConvention(TestCase):

    def test_scope(self):
        with SBConvention():
            self.assertIs(SBConvention, NamingConvention.get())

    def test_decompose_string(self):
        name = "R_arm_shoulder_geo"
        n = SBConvention.decompose(name)
        self.assertIsInstance(n, NameComposition)
        self.assertEqual(name, n.name())

    def test_decompose_stringlike(self):
        name = 42  # str(42) == "None"
        n = SBConvention.decompose(name)
        self.assertIsInstance(n, NameComposition)
        self.assertEqual("42", n.name())

    def test_decompose_emptyString(self):
        name = ""
        with self.assertRaises(ValueError):
            SBConvention.decompose(name)

    def test_compose_unknown(self):
        with self.assertRaises(UnknownComponentError):
            SBConvention.compose(unknown="value")

    def test_compose_missing_side(self):
        with self.assertRaises(ValueError):
            SBConvention.compose(module="arm", basename="shoulder", type="geo")

    def test_compose_missing_module(self):
        with self.assertRaises(ValueError):
            SBConvention.compose(side="R", basename="shoulder", type="geo")

    def test_compose_missing_basename(self):
        with self.assertRaises(ValueError):
            SBConvention.compose(side="R", module="arm", type="geo")

    def test_compose_missing_type(self):
        with self.assertRaises(ValueError):
            SBConvention.compose(side="R", module="arm", basename="shoulder")

    def test_compose_success(self):
        n = SBConvention.compose(side="R", module="arm", basename="shoulder", type="geo")
        self.assertIsInstance(n, NameComposition)
        self.assertEqual("R_arm_shoulder_geo", n.name())

    def test_compose_success_desc(self):
        n = SBConvention.compose(side="R", module="arm", basename="shoulder", desc="description", type="geo")
        self.assertIsInstance(n, NameComposition)
        self.assertEqual("R_arm_shoulder_description_geo", n.name())

    def test_compose_success_stringlike(self):
        n = SBConvention.compose(side=1, module=2, basename=3, desc=4, type=5)
        self.assertIsInstance(n, NameComposition)
        self.assertEqual("1_2_3_4_5", n.name())

class TestSBName(TestCase):

    # name tests #

    def test_name(self):
        n = SBName("name")
        self.assertEqual("name", n.name())

    def test_str(self):
        n = SBName("name")
        self.assertEqual("name", str(n))

    # getter tests #

    def test_side(self):
        n = SBName(side="R")
        self.assertEqual("R", n.side())

    def test_side_missing(self):
        n = SBName(module="arm", basename="shoulder", desc="description", type="geo")
        self.assertIsNone(n.side())

    def test_module(self):
        n = SBName(module="arm")
        self.assertEqual("arm", n.module())

    def test_module_missing(self):
        n = SBName(side="R", basename="shoulder", desc="description", type="geo")
        self.assertIsNone(n.module())

    def test_basename(self):
        n = SBName(basename="knee")
        self.assertEqual("knee", n.basename())

    def test_basename_missing(self):
        n = SBName(side="R", module="arm", desc="description", type="geo")
        self.assertIsNone(n.basename())

    def test_desc(self):
        n = SBName(desc="blah")
        self.assertEqual("blah", n.description())

    def test_desc_unset(self):
        n = SBName(side="R", module="arm", basename="shoulder", type="geo")
        self.assertIsNone(n.description())

    def test_type(self):
        n = SBName(type="geo")
        self.assertEqual("geo", n.type())

    def test_type_missing(self):
        n = SBName(side="R", module="arm", basename="shoulder", desc="description")
        self.assertIsNone(n.type())

    # getComponent tests #

    def test_getComponent_side(self):
        n = SBName(side="R")
        self.assertEqual("R", n.getComponent("side"))

    def test_getComponent_side_missing(self):
        n = SBName(module="arm", basename="shoulder", desc="description", type="geo")
        self.assertIsNone(n.getComponent("side"))

    def test_getComponent_module(self):
        n = SBName(module="leg")
        self.assertEqual("leg", n.getComponent("module"))

    def test_getComponent_module_missing(self):
        n = SBName(side="R", basename="shoulder", desc="description", type="geo")
        self.assertIsNone(n.getComponent("module"))

    def test_getComponent_basename(self):
        n = SBName(basename="hip")
        self.assertEqual("hip", n.getComponent("basename"))

    def test_getComponent_basename_missing(self):
        n = SBName(side="R", module="arm", desc="description", type="geo")
        self.assertIsNone(n.getComponent("basename"))

    def test_getComponent_desc(self):
        n = SBName(desc="blah")
        self.assertEqual("blah", n.getComponent("desc"))

    def test_getComponent_desc_unset(self):
        n = SBName(side="R", module="arm", basename="shoulder", type="geo")
        self.assertIsNone(n.getComponent("desc"))

    def test_getComponent_type(self):
        n = SBName(type="Grp")
        self.assertEqual("Grp", n.getComponent("type"))

    def test_getComponent_type_missing(self):
        n = SBName(side="R", module="arm", basename="shoulder", desc="description")
        self.assertIsNone(n.getComponent("type"))

    def test_getComponent_unknown(self):
        n = SBName()
        with self.assertRaises(UnknownComponentError):
            n.getComponent("unknown")

    # replace tests #

    def test_replace_basic(self):
        n   =    SBName(side="R", module="arm", basename="shoulder",                     type="geo")
        r   = n.replace(side="L",                                    desc="description")
        exp =    SBName(side="L", module="arm", basename="shoulder", desc="description", type="geo")
        self.assertEqual(exp.name(), r.name())
        self.assertIsInstance(r, SBName)

    def test_replace_none(self):
        n   =    SBName(side="R", module="arm", basename="shoulder", desc="description", type="geo")
        r   = n.replace()
        exp =    SBName(side="R", module="arm", basename="shoulder", desc="description", type="geo")
        self.assertEqual(exp.name(), r.name())

    def test_replace_all(self):
        n   =    SBName(side="R", module="arm", basename="shoulder", desc="desc",        type="geo")
        r   = n.replace(side="L", module="leg", basename="knee",     desc="description", type="Grp")
        exp =    SBName(side="L", module="leg", basename="knee",     desc="description", type="Grp")
        self.assertEqual(exp.name(), r.name())

    def test_replace_missing(self):
        n   =    SBName()
        r   = n.replace(side="L", module="leg", basename="knee", desc="description", type="Grp")
        exp =    SBName(side="L", module="leg", basename="knee", desc="description", type="Grp")
        self.assertEqual(exp.name(), r.name())

    def test_replace_stringlike(self):
        n   =    SBName(side="R", module="arm", basename="shoulder", desc="description", type="geo")
        r   = n.replace(side=1,   module=2,     basename=3,          desc=4,             type=5)
        exp =    SBName(side="1", module="2",   basename="3",        desc="4",           type="5")
        self.assertEqual(exp.name(), r.name())

    def test_replace_unknown(self):
        n = SBName(side="R", module="arm", basename="shoulder", desc="description", type="geo")
        with self.assertRaises(UnknownComponentError) as raised:
            n.replace(unknown="value")
        self.assertListEqual(["unknown"], raised.exception.components)

    # name composition tests #

    def test_name_only_side(self):
        n = SBName(side="side")
        self.assertEqual("side", n.name())

    def test_name_only_module(self):
        n = SBName(module="module")
        self.assertEqual("module", n.name())

    def test_name_only_basename(self):
        n = SBName(basename="basename")
        self.assertEqual("basename", n.name())

    def test_name_only_desc(self):
        n = SBName(desc="desc")
        self.assertEqual("desc", n.name())

    def test_name_only_type(self):
        n = SBName(type="type")
        self.assertEqual("type", n.name())

    def test_name_empty(self):
        n = SBName()
        self.assertEqual("", n.name())

    def test_name_all_required(self):
        n = SBName(side="R", module="arm", basename="shoulder", type="geo")
        self.assertEqual("R_arm_shoulder_geo", n.name())

    def test_name_all_with_multiple_words(self):
        n = SBName(side="R", module="arm", basename="shoulder", desc="three_word_desc", type="ik_ctrl")
        self.assertEqual("R_arm_shoulder_three_word_desc_ik_ctrl", n.name())

    # isValid tests #

    def test_isValid_success(self):
        n = SBName(side="R", module="arm", basename="shoulder", type="ctrl")
        self.assertTrue(n.isValid())

    def test_isValid_success_with_desc(self):
        n = SBName(side="R", module="arm", basename="shoulder", desc="three_word_desc", type="ctrl")
        self.assertTrue(n.isValid())

    def test_isValid_success_basename_with_digits(self):
        n = SBName(side="R", module="arm", basename="99problems", desc="desc", type="ctrl")
        self.assertTrue(n.isValid())

    def test_isValid_success_desc_with_digits(self):
        n = SBName(side="R", module="arm", basename="shoulder", desc="9_2_5", type="ctrl")
        self.assertTrue(n.isValid())

    def test_isValid_bad_name(self):
        n = SBName(side="R", module="arm", basename="^bad", type="ctrl")
        self.assertFalse(n.isValid())

    def test_isValid_missing_side(self):
        n = SBName(module="arm", basename="shoulder", desc="desc", type="ctrl")
        self.assertFalse(n.isValid())

    def test_isValid_missing_module(self):
        n = SBName(side="R", basename="shoulder", desc="desc", type="ctrl")
        self.assertFalse(n.isValid())

    def test_isValid_missing_basename(self):
        n = SBName(side="R", module="arm", desc="desc", type="ctrl")
        self.assertFalse(n.isValid())

    def test_isValid_missing_type(self):
        n = SBName(side="R", module="arm", basename="shoulder", desc="desc")
        self.assertFalse(n.isValid())

    def test_isValid_empty_side(self):
        n = SBName(side="", module="arm", basename="shoulder", desc="desc", type="ctrl")
        self.assertFalse(n.isValid())

    def test_isValid_empty_module(self):
        n = SBName(side="R", module="", basename="shoulder", desc="desc", type="ctrl")
        self.assertFalse(n.isValid())

    def test_isValid_empty_basename(self):
        n = SBName(side="R", module="arm", basename="", desc="desc", type="ctrl")
        self.assertFalse(n.isValid())

    def test_isValid_empty_desc(self):
        n = SBName(side="R", module="arm", basename="shoulder", desc="", type="ctrl")
        self.assertFalse(n.isValid())

    def test_isValid_empty_type(self):
        n = SBName(side="R", module="arm", basename="shoulder", desc="desc", type="")
        self.assertFalse(n.isValid())

    def test_isValid_undefined_side(self):
        n = SBName(side="badValue42", module="arm", basename="shoulder", desc="desc", type="ctrl")
        self.assertFalse(n.isValid())

    def test_isValid_undefined_module(self):
        n = SBName(side="R", module="badValue42", basename="shoulder", desc="desc", type="ctrl")
        self.assertFalse(n.isValid())

    def test_isValid_undefined_type(self):
        n = SBName(side="R", module="arm", basename="shoulder", desc="desc", type="badValue42")
        self.assertFalse(n.isValid())

    def test_isValid_underscore_in_basename(self):
        n = SBName(side="R", module="arm", basename="two_words", desc="desc", type="ctrl")
        self.assertFalse(n.isValid())

    def test_isValid_underscores_delimiters(self):
        n = SBName(side="R", module="arm", basename="shoulder", desc="_desc_", type="ctrl")
        self.assertFalse(n.isValid())

    # decomposition tests #

    def assertDecomposition(self, name, side=None, module=None, basename=None, desc=None, type=None):
        n = SBName(name)
        self.assertEqual(side,     n.side(),         "'{0}'.side != '{1}' (was '{2}')".format(name, side, n.side()))
        self.assertEqual(module,   n.module(),       "'{0}'.module != '{1}' (was '{2}')".format(name, module, n.module()))
        self.assertEqual(basename, n.basename(),     "'{0}'.basename != '{1}' (was '{2}')".format(name, basename, n.basename()))
        self.assertEqual(desc,     n.description(),  "'{0}'.desc != '{1}' (was '{2}')".format(name, desc, n.description()))
        self.assertEqual(type,     n.type(),         "'{0}'.type != '{1}' (was '{2}')".format(name, type, n.type()))

    def test_decompose_complete_basic(self):
        self.assertDecomposition("R_arm_shoulder_ctrl", side="R", module="arm", basename="shoulder",          type="ctrl")
        self.assertDecomposition("L_leg_knee_desc_Grp", side="L", module="leg", basename="knee", desc="desc", type="Grp")

    def test_decompose_complete_multiword_type(self):
        self.assertDecomposition("R_leg_knee_IK_ctrl",      side="R", module="leg", basename="knee",              type="IK_ctrl")
        self.assertDecomposition("R_leg_knee_desc_IK_ctrl", side="R", module="leg", basename="knee", desc="desc", type="IK_ctrl")
        self.assertDecomposition("R_leg_knee_FIK_ctrl",     side="R", module="leg", basename="knee", desc="FIK",  type="ctrl")

    def test_decompose_complete_invalid(self):
        self.assertDecomposition("42_is_a_number",            side="42", module="is", basename="a",                    type="number")
        self.assertDecomposition("42_is_a_great_number",      side="42", module="is", basename="a", desc="great",      type="number")
        self.assertDecomposition("42_is_a_very_great_number", side="42", module="is", basename="a", desc="very_great", type="number")

    def test_decompose_complete_empty(self):
        self.assertDecomposition("___",    side="", module="", basename="",            type="")
        self.assertDecomposition("____",   side="", module="", basename="", desc="",   type="")
        self.assertDecomposition("_____",  side="", module="", basename="", desc="_",  type="")
        self.assertDecomposition("______", side="", module="", basename="", desc="__", type="")

    def test_decompose_incomplete_empty(self):
        self.assertDecomposition("",   basename="")
        self.assertDecomposition("_",  basename="", desc="")
        self.assertDecomposition("__", basename="", desc="_")

    def test_decompose_incomplete_one(self):
        self.assertDecomposition("R",        side="R")
        self.assertDecomposition("arm",      module="arm")
        self.assertDecomposition("Grp",      type="Grp")
        self.assertDecomposition("basename", basename="basename")

    def test_decompose_incomplete_one_casing_variant(self):
        self.assertDecomposition("JNT", type="JNT")
        self.assertDecomposition("r",   side="r")
        self.assertDecomposition("ARM", module="ARM")

    def test_decompose_incomplete_two(self):
        self.assertDecomposition("R_arm",      side="R", module="arm")
        self.assertDecomposition("R_basename", side="R", basename="basename")
        self.assertDecomposition("R_Grp",      side="R", type="Grp")
        self.assertDecomposition("arm_basename", module="arm", basename="basename")
        self.assertDecomposition("arm_Grp",      module="arm", type="Grp")
        self.assertDecomposition("basename_Grp",  basename="basename", type="Grp")
        self.assertDecomposition("basename_desc", basename="basename", desc="desc")
        self.assertDecomposition("IK_ctrl", type="IK_ctrl")

    def test_decompose_incomplete_two_casing_variant(self):
        self.assertDecomposition("r_Arm",      side="r", module="Arm")
        self.assertDecomposition("r_basename", side="r", basename="basename")
        self.assertDecomposition("l_JNT",      side="l", type="JNT")
        self.assertDecomposition("Leg_basename", module="Leg", basename="basename")
        self.assertDecomposition("arm_CTRL",     module="arm", type="CTRL")
        self.assertDecomposition("basename_GRP", basename="basename", type="GRP")
        self.assertDecomposition("ik_Ctrl", type="ik_Ctrl")

    def test_decompose_incomplete_three(self):
        self.assertDecomposition("R_arm_basename",  side="R", module="arm", basename="basename")
        self.assertDecomposition("R_arm_Grp",       side="R", module="arm", type="Grp")
        self.assertDecomposition("R_basename_Grp",  side="R", basename="basename", type="Grp")
        self.assertDecomposition("R_basename_desc", side="R", basename="basename", desc="desc")
        self.assertDecomposition("R_IK_ctrl",       side="R", type="IK_ctrl")
        self.assertDecomposition("arm_basename_Grp",  module="arm", basename="basename", type="Grp")
        self.assertDecomposition("arm_basename_desc", module="arm", basename="basename", desc="desc")
        self.assertDecomposition("arm_IK_ctrl",       module="arm", type="IK_ctrl")
        self.assertDecomposition("basename_desc_Grp",  basename="basename", desc="desc", type="Grp")
        self.assertDecomposition("basename_desc_desc", basename="basename", desc="desc_desc")
        self.assertDecomposition("basename_IK_ctrl",   basename="basename", type="IK_ctrl")

