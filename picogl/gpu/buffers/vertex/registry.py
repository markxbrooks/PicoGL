"""
A module for managing OpenGL object information.

This module defines a data structure for representing OpenGL object info,
and provides a registry to store and manage these objects. It includes
details such as object handle, type, label, creation time, and associated
attributes.
"""

import os
import time
from collections import Counter
from dataclasses import dataclass, field
from typing import Dict, Optional

from decologr import Decologr as log
from PySide6 import QtGui


class GLObjectAttrs:
    """gl Object Attributes"""

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
        GLObjectAttrs.current_context, id(QtGui.QOpenGLContext.currentContext())
    )


def dump_gl_registry(verbose: Optional[bool] = None) -> None:
    """Log registered VAOs on shutdown.

    * Always logs a sorted **summary** (counts by label) to the logger and **prints** that
      line to stdout so it stays visible above profilers or truncated IDE output.
    * Logs one line **per VAO** at INFO by default (same as pre-summary behaviour).

    * ``DUMP_GL_REGISTRY_QUIET=1`` — summary only (no per-VAO lines).
    * ``DUMP_GL_REGISTRY_VERBOSE=0`` — same as quiet (optional alias).
    * Force full listing: pass ``verbose=True`` (overrides quiet).
    """
    if verbose is None:
        quiet = os.environ.get("DUMP_GL_REGISTRY_QUIET", "").strip().lower() in (
            "1",
            "true",
            "yes",
        ) or os.environ.get("DUMP_GL_REGISTRY_VERBOSE", "").strip().lower() in (
            "0",
            "false",
            "no",
        )
        verbose = not quiet

    if not GL_REGISTRY:
        msg = "gl registry: empty"
        log.info(msg, scope="dump_gl_registry")
        print(f"[dump_gl_registry] {msg}", flush=True)
        return

    by_label = Counter(info.label for info in GL_REGISTRY.values())
    ctx_ids = {info.context_id for info in GL_REGISTRY.values()}
    breakdown = ", ".join(
        f"{label}={n}"
        for label, n in sorted(by_label.items(), key=lambda x: (-x[1], x[0]))
    )
    summary = (
        f"gl registry: {len(GL_REGISTRY)} VAO(s), {len(ctx_ids)} context id(s). "
        f"By label: {breakdown}"
    )
    log.info(summary, scope="dump_gl_registry")
    print(f"[dump_gl_registry] {summary}", flush=True)

    if verbose:
        for obj in sorted(GL_REGISTRY.values(), key=lambda i: i.handle):
            log.info(
                f"{obj.type} {obj.handle} label={obj.label} "
                f"context={obj.context_id}",
                scope="dump_gl_registry",
            )


def store_in_gl_registry(
    handle: int, label: str, ctx_id: int, buffer_type: str = "VAO"
):
    """store in gl registry"""
    GL_REGISTRY[handle] = GLObjectInfo(
        handle=handle, type=buffer_type, label=label, context_id=ctx_id
    )
