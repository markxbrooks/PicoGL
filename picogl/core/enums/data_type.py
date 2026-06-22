"""
Defines a compatibility shim for deprecated GL data types.

This module provides a compatibility layer for GL numeric data types by
associating GLNumeric with the alias GLDataType. It serves as a stopgap
solution for maintaining backward compatibility in scenarios where
GLDataType is still referenced.
"""


from picogl.core.enums.numerical import GLNumeric

"""Compatibility shim"""
GLDataType = GLNumeric # Deprecated
