from typing import Any, Union, NewType

import maya.OpenMaya as om

__all__ = [
    "Pattern",
    "PatternLike",
    "Identifier",
    "Placeholder",
    "placeholder",
]

Pattern = str
"""
A pattern identifies one or more Maya nodes by their name (DAG path).
It may contain wildcards. The special value "<world>" identifies the
Maya world node.
"""

PatternLike = Any
"""
Any type that can be resolved to a Pattern by conversion via str(...).
"""

Identifier = Union[Pattern, om.MUuid]
"""
An identifier is either a pattern or an OpenMaya uuid object. It is
the intention that an identifier uniquely identifies a single subject.
"""

Placeholder = NewType("Placeholder", object)
"""
A placeholder marks the lack of a value, just like None.
It can be used to denote lazily computed types Union[T, Placeholder] that
either is some computed value of type T or the placeholder value of type
Placeholder that represents the lack of a value.
"""

placeholder: Placeholder = Placeholder(object())
"""
The only value of Placeholder.
"""
