"""
A module for managing OpenGL object information.

This module defines a data structure for representing OpenGL object info,
and provides a registry to store and manage these objects. It includes
details such as object handle, type, label, creation time, and associated
attributes.
"""

from dataclasses import dataclass, field
from typing import Dict, Optional
import time

from PySide6 import QtGui
from decologr import Decologr as log


class GLObjectAttrs:
    """GL Object Attributes"""
    handle = "handle"
    label = "label"
    created_context = "created_context"
    current_context = "current_context"


@dataclass
class GLObjectInfo:
    handle: int
    type: str
    label: str
    created_at: float = field(default_factory=time.time)
    context_id: Optional[int] = None
    attributes: dict = field(default_factory=dict)

GL_REGISTRY: Dict[int, GLObjectInfo] = {}


def debug_vao(vao):
    info = GL_REGISTRY.get(vao)

    if not info:
        log.error(f"VAO {vao} not found in registry")
        return

    log.error("VAO DEBUG INFO")
    log.parameter(GLObjectAttrs.handle, info.handle)
    log.parameter(GLObjectAttrs.label, info.label)
    log.parameter(GLObjectAttrs.created_context, info.context_id)
    log.parameter(
        GLObjectAttrs.current_context,
        id(QtGui.QOpenGLContext.currentContext())
    )


def dump_gl_registry():
    print(GL_REGISTRY)
    for obj in GL_REGISTRY.values():
        log.info(
            f"{obj.type} {obj.handle} label={obj.label} "
            f"context={obj.context_id}", scope="dump_gl_registry"
        )


def store_in_gl_registry(handle: int, label: str, ctx_id: int, buffer_type: str = "VAO"):
    """store in gl registry"""
    GL_REGISTRY[handle] = GLObjectInfo(handle=handle, type=buffer_type, label=label,
                                            context_id=ctx_id)
