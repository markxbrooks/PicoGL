"""
ShaderManager
=============

Manages ``ShaderType → ShaderProgram`` lookup, optional eager warm-up, and the
currently bound program. Compilation is lazy on :meth:`get`; call
:meth:`initialize_shaders` during ``initializeGL`` for startup diagnostics.

Example::

    shader_manager = ShaderManager()
    shader_manager.initialize_shaders()

    shader = shader_manager.use(ShaderType.ATOMS)
    if shader is not None:
        shader.set_mvp(my_mvp_matrix)
        shader.set_uniform("point_size", 15.0)

File naming convention:
=======================
Ensure GLSL files follow the naming pattern:

atoms_vert.glsl
atoms_frag.glsl
bonds_vert.glsl
bonds_frag.glsl
"""

from __future__ import annotations

import warnings
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Callable, Dict, Iterable, Optional, Tuple, Union

import numpy as np
from decologr import Decologr as log
from pyglm import glm

from picogl.backend.modern.core.shader.context import gl_context_available
from picogl.backend.modern.core.shader.program import ShaderProgram
from picogl.globals import PICOGL_SHADER_SRC_DIRECTORY
from picogl.shaders.loader import ShaderLoader
from picogl.shaders.type import ShaderType
from picogl.backend.gl.api.shader import gl_use_program

SILENT_SHADER = True


class ShaderManagerState(Enum):
    """Lifecycle of optional eager warm-up (lazy load works in any state)."""

    UNINITIALIZED = auto()
    WARMING = auto()
    READY = auto()
    RELEASED = auto()


def _progress_iter(
    pairs: Iterable[Tuple[int, ShaderType]], *, desc: str, total: int
) -> Iterable[Tuple[int, ShaderType]]:
    """Optional tqdm in real terminals only; GUI apps use plain iteration."""
    import sys

    if not sys.stderr.isatty():
        return pairs
    try:
        from tqdm.rich import tqdm
    except ImportError:
        try:
            from tqdm import tqdm
        except ImportError:
            return pairs
    return tqdm(
        pairs,
        desc=desc,
        total=total,
        unit="shader",
        leave=False,
        monitor_interval=0,
    )


@dataclass
class ShaderManager:
    """
    Repository and binding state for modern shader programs.

    ``shaders`` holds only successfully compiled programs. Failed types are
    tracked in ``_failed`` and resolved via :meth:`resolve` using the fallback
    program.
    """

    shaders: Dict[ShaderType, ShaderProgram] = field(default_factory=dict)
    default_shader_type: ShaderType = ShaderType.DEFAULT
    current_shader_type: ShaderType = ShaderType.DEFAULT
    current_shader: ShaderProgram | None = None
    shader_directory: str = ""
    fallback_shader_directory: str = ""
    _state: ShaderManagerState = field(default=ShaderManagerState.UNINITIALIZED, repr=False)
    _failed: set[ShaderType] = field(default_factory=set, repr=False)
    _loader: ShaderLoader | None = field(default=None, repr=False)

    @property
    def current_shader_program(self) -> int | None:
        """OpenGL program id of :attr:`current_shader`, or ``None``."""
        if self.current_shader is None:
            return None
        return self.current_shader.program_id()

    @property
    def fallback_shader(self) -> ShaderProgram | None:
        """Shared fallback program (compiled lazily)."""
        loader = self._ensure_loader()
        return loader.fallback.program()

    @property
    def _initialized(self) -> bool:
        return self._state == ShaderManagerState.READY

    @_initialized.setter
    def _initialized(self, value: bool) -> None:
        if value:
            self._state = ShaderManagerState.READY
        elif self._state == ShaderManagerState.READY:
            self._state = ShaderManagerState.UNINITIALIZED

    @property
    def _initializing(self) -> bool:
        return self._state == ShaderManagerState.WARMING

    def _ensure_loader(self) -> ShaderLoader:
        if self._loader is None:
            self._loader = ShaderLoader(
                self.shader_directory or str(PICOGL_SHADER_SRC_DIRECTORY)
            )
        return self._loader

    def bind(self, shader: ShaderProgram) -> None:
        """Bind *shader* and record it as current (no loading or warm-up)."""
        if not shader:
            log.error("Cannot bind: shader is None or invalid", scope="ShaderManager")
            return
        try:
            shader.bind()
            self.current_shader = shader
        except RuntimeError as ex:
            log.warning(f"Shader bind skipped: {ex}", scope="ShaderManager")
        except Exception as ex:
            log.error(f"Failed to bind shader: {ex}", scope="ShaderManager")

    def use_shader_program(self, shader_program: ShaderProgram) -> None:
        """Deprecated alias for :meth:`bind`."""
        self.bind(shader_program)

    def unbind(self) -> None:
        """Unbind the active program."""
        gl_use_program(0)
        self.current_shader = None

    def get(self, shader_type: ShaderType) -> ShaderProgram | None:
        """Return a compiled program for *shader_type*, loading on cache miss."""
        cached = self.shaders.get(shader_type)
        if cached is not None:
            return cached
        if shader_type in self._failed:
            return None
        if not gl_context_available():
            return None
        return self._load(shader_type)

    def get_shader_type(self, shader_type: ShaderType) -> ShaderProgram | None:
        """Deprecated alias for :meth:`get`."""
        return self.get(shader_type)

    def resolve(self, shader_type: ShaderType) -> ShaderProgram | None:
        """Return the program for *shader_type*, or the fallback if load failed."""
        return self.get(shader_type) or self._fallback_program()

    def used_fallback_for(self, shader_type: ShaderType) -> bool:
        """``True`` when *shader_type* failed to compile and fallback would be used."""
        return shader_type in self._failed

    def failed_types(self) -> frozenset[ShaderType]:
        """Shader types that failed compilation during warm-up or lazy load."""
        return frozenset(self._failed)

    def use(self, shader_type: ShaderType) -> ShaderProgram | None:
        """Resolve, bind, and return the program for *shader_type*."""
        shader = self.resolve(shader_type)
        if shader is None:
            log.error(
                f"Shader type {shader_type} could not be loaded or bound.",
                scope=self.__class__.__name__,
            )
            return None
        self.bind(shader)
        if self.current_shader is not shader:
            return None
        self.current_shader_type = shader_type
        return shader

    def use_shader_type(
        self,
        shader_type: ShaderType,
        mvp_matrix: np.ndarray | glm.mat4 | None = None,
        zoom_scale: int | float | None = None,
    ) -> bool:
        """
        Resolve and bind *shader_type*.

        ``mvp_matrix`` and ``zoom_scale`` are deprecated; set uniforms on the
        returned :class:`ShaderProgram` via :meth:`use` instead.
        """
        if mvp_matrix is not None or zoom_scale is not None:
            warnings.warn(
                "use_shader_type(mvp_matrix=..., zoom_scale=...) is deprecated; "
                "use shader_manager.use(type) then shader.set_mvp(...) / "
                "set_uniform(...)",
                DeprecationWarning,
                stacklevel=2,
            )
        shader = self.use(shader_type)
        if shader is None:
            return False
        if mvp_matrix is not None:
            self.update_mvp_uniform(mvp_matrix=mvp_matrix)
        if zoom_scale is not None:
            shader.set_uniform("zoom_scale", zoom_scale)
        return True

    def update_mvp_uniform(self, mvp_matrix: np.ndarray | glm.mat4) -> None:
        """Deprecated: delegate to :attr:`current_shader`."""
        if self.current_shader is None:
            return
        self.current_shader.set_mvp(mvp_matrix)

    def set_uniform_value(
        self,
        uniform_name: str,
        uniform_value: Union[
            float, int, glm.vec2, glm.vec3, glm.vec4, glm.mat4, np.ndarray
        ],
    ) -> None:
        """Deprecated: delegate to :attr:`current_shader`."""
        if self.current_shader is None:
            return
        self.current_shader.set_uniform(uniform_name, uniform_value)
        log.message(
            f"setting {self.current_shader.shader_name} uniform {uniform_name} "
            f"to value {uniform_value}",
            silent=SILENT_SHADER,
        )

    def use_default_shader(
        self, mvp_matrix: np.ndarray | glm.mat4 | None = None
    ) -> None:
        """Bind the default shader type."""
        if mvp_matrix is not None:
            self.use_shader_type(
                shader_type=self.default_shader_type, mvp_matrix=mvp_matrix
            )
        else:
            self.use(self.default_shader_type)

    def initialize_shaders(
        self,
        shader_dir: str | None = None,
        *,
        on_shader_loaded: Callable[[int, int, ShaderType], None] | None = None,
    ) -> None:
        """Eager warm-up: compile all :class:`ShaderType` values when GL context exists."""
        if shader_dir:
            target_dir = str(shader_dir)
        elif self.shader_directory:
            target_dir = str(self.shader_directory)
        else:
            target_dir = str(PICOGL_SHADER_SRC_DIRECTORY)

        if self._state == ShaderManagerState.READY:
            if target_dir == str(self.shader_directory):
                return
            self.release_shaders()

        if not gl_context_available():
            log.warning(
                "ShaderManager.initialize_shaders deferred: no current OpenGL context. "
                "Load shaders from initializeGL / paintGL after the gl widget context is current.",
                scope="ShaderManager",
            )
            return

        if self._state == ShaderManagerState.WARMING:
            return

        self._state = ShaderManagerState.WARMING
        try:
            self.shader_directory = target_dir
            loader = self._ensure_loader()
            loader.set_directory(target_dir)
            self._warm_up_all(on_shader_loaded=on_shader_loaded)

            failed = [st for st in ShaderType if st in self._failed]
            if failed:
                log.warning(
                    f"Shader fallback will be used for: "
                    f"{', '.join(st.value for st in failed)}",
                    scope="ShaderManager",
                )

            log.message(
                "Shader sources loaded (fallback available for failed types).",
                scope="ShaderManager",
                silent=True,
            )
            default_shader = self.resolve(self.default_shader_type)
            if default_shader:
                self.bind(default_shader)
                if self.current_shader is default_shader:
                    self.current_shader_type = self.default_shader_type
                    self._state = ShaderManagerState.READY
            if self._state != ShaderManagerState.READY:
                log.error(
                    "ShaderManager: default shader could not be bound; "
                    "modern rendering will stay disabled until gl init succeeds.",
                    scope="ShaderManager",
                )
        finally:
            if self._state == ShaderManagerState.WARMING:
                self._state = ShaderManagerState.UNINITIALIZED

    def _warm_up_all(
        self,
        *,
        on_shader_loaded: Callable[[int, int, ShaderType], None] | None = None,
    ) -> None:
        shader_pairs = list(enumerate(ShaderType))
        n = len(shader_pairs)
        for shader_number, shader_type in _progress_iter(
            shader_pairs, desc="Shader programs", total=n
        ):
            log.message(
                f"Loading shader type: '{shader_type.value}' from {self.shader_directory}",
                silent=True,
                scope="ShaderManager",
            )
            self._load(shader_type)
            if on_shader_loaded is not None:
                try:
                    on_shader_loaded(shader_number, n, shader_type)
                except Exception:
                    pass

    def load_shader(self, shader_type: ShaderType, shader_number: int = 0) -> None:
        """Public compile hook (used by warm-up and tests)."""
        self._load(shader_type)

    def _load(self, shader_type: ShaderType) -> ShaderProgram | None:
        if shader_type in self.shaders:
            return self.shaders[shader_type]
        if shader_type in self._failed:
            return None
        if not gl_context_available():
            return None
        if self.shader_directory:
            self._ensure_loader().set_directory(self.shader_directory)
        result = self._ensure_loader().load(shader_type)
        if result.shader is not None:
            self.shaders[shader_type] = result.shader
            return result.shader
        self._failed.add(shader_type)
        return None

    def _fallback_program(self) -> ShaderProgram | None:
        loader = self._ensure_loader()
        if self.shader_directory:
            loader.set_directory(self.shader_directory)
        return loader.fallback.program()

    def release_shaders(self) -> None:
        """Release all compiled programs and reset manager state."""
        for shader in self.shaders.values():
            try:
                shader.release()
            except Exception:
                pass
        self.shaders.clear()
        self._failed.clear()
        if self._loader is not None:
            self._loader.fallback.release()
        self._loader = None
        self.current_shader = None
        self._state = ShaderManagerState.RELEASED
