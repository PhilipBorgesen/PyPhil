from typing import Any, Union

import maya.OpenMaya as om

__all__ = [
    "Pattern",
    "PatternLike",
    "Identifier",
]

"""
A pattern identifies one or more Maya nodes by their name (DAG path).
It may contain wildcards. The special value "<world>" identifies the
Maya world node.
"""
Pattern = str

"""
Any type that can be resolved to a Pattern by conversion via str(...).
"""
PatternLike = Any

"""
An identifier is either a pattern or an OpenMaya uuid object. It is
the intention that an identifier uniquely identifies a single subject.
"""
Identifier = Union[Pattern, om.MUuid]
