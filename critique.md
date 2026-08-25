# ShaderManager Critique

Overall, I think this is a substantial improvement over a typical ad-hoc shader loader, but I would not keep it in its current form. The main issue is that ShaderManager is currently doing too many jobs: resource discovery, compilation, fallback policy, OpenGL context lifecycle, program binding, current-state tracking, uniform management, progress reporting, and error recovery.

The good news is that the underlying design is quite salvageable.

What I like

The core responsibility is clear:

ShaderType → ShaderProgram

The dictionary is the right fundamental structure:

shaders: Dict[ShaderType, ShaderProgram]

and the separation between loading and binding is mostly sensible. In particular, these are good concepts:

ShaderType as the semantic identifier
lazy get_shader_type()
explicit use_shader_type()
a fallback shader
_initialized / _initializing protection
checking gl_context_available() before compilation
explicit release_shaders()
keeping ShaderProgram responsible for actual program operations

The context check is especially appropriate given the OpenGL/Qt problems you've been dealing with. initialize_shaders() explicitly deferring when there is no current context is much safer than allowing construction-time GL calls.

Likewise, having a fallback rather than letting one bad GLSL program take down the entire renderer is a reasonable robustness policy.

The biggest problem: it is really 3–4 classes

At present ShaderManager contains roughly these responsibilities:

1. Shader repository
self.shaders
get()
get_shader_type()
2. Shader compilation/loading
initialize_shaders()
load_shader()
_fallback_shader_sources()
_ensure_fallback()
3. OpenGL program state
bind()
unbind()
use_shader_program()
current_shader
current_shader_program
current_shader_type
4. Uniform API
update_mvp_uniform()
set_uniform_value()

And then there's a fifth concern:

5. Application policy
use_default_shader()
_progress_iter()
on_shader_loaded
fallback behaviour

That's why the class is already at ~370 lines despite its apparently simple purpose.

I would aim for:

ShaderManager
    │
    ├── ShaderRepository
    │       └── ShaderType → ShaderProgram
    │
    ├── ShaderLoader
    │       ├── source loading
    │       ├── compilation
    │       └── fallback
    │
    └── ShaderBinding / ShaderState
            └── current program

But I would not necessarily implement all three immediately. There is a simpler refactoring that gets most of the benefit.

1. current_shader and current_shader_program are redundant

This is probably the first thing I'd change.

You currently maintain:

current_shader: Optional[ShaderProgram] = None
current_shader_program: Optional[int] = None

but the second is completely derivable:

current_shader.program

So you have two pieces of state that can become inconsistent.

For example:

self.current_shader = shader
self.current_shader_program = shader.program

appears in multiple places.

I'd reduce this to:

current_shader: ShaderProgram | None = None

and expose:

@property
def current_program(self) -> int | None:
    return self.current_shader.program if self.current_shader else None

Or, even better, rename it:

@property
def current_shader_program(self) -> int | None:
    ...

Then callers don't need to know that the manager internally stores a ShaderProgram.

This is particularly valuable in your architecture because you are trying to separate OpenGL abstraction from renderer logic.

2. bind() and use_shader_program() are essentially duplicates

You have:

def use_shader_program(...)

and:

def bind(...)

The former does:

shader_program.bind()
self.current_shader = shader_program
self.current_shader_program = shader_program.program

The latter does essentially the same thing.

That should become one method.

I'd use:

def bind(self, shader: ShaderProgram) -> None:
    shader.bind()
    self.current_shader = shader

Then use_shader_type() becomes:

def use_shader_type(self, shader_type: ShaderType) -> bool:
    shader = self.get(shader_type)

    if shader is None:
        return False

    self.bind(shader)
    self.current_shader_type = shader_type
    return True

Much cleaner.

3. get_shader_type() has unnecessary logic

This:

cached = self.shaders.get(shader_type)
if cached is not None:
    return cached

if shader_type not in self.shaders:
    shader_number = list(ShaderType).index(shader_type)
    self.load_shader(shader_type, shader_number)
    return self.shaders.get(shader_type)

return None

is effectively:

shader = self.shaders.get(shader_type)

if shader is None:
    self.load_shader(shader_type)

return self.shaders.get(shader_type)

The if shader_type not in self.shaders branch is redundant.

Also:

list(ShaderType).index(shader_type)

is a smell.

The shader number isn't really a property of the shader manager. If you need an index for logging/progress, enumerate at the caller and pass it through only for progress reporting.

Even better, make:

load_shader(shader_type)

and let the loader know nothing about shader numbering.

4. I would strongly question initialize_shaders() doing eager loading

This is the architectural point I'd think hardest about.

You have lazy loading:

get_shader_type()

but then initialize_shaders() explicitly does:

for shader_number, shader_type in ...:
    self.load_shader(shader_type, shader_number)

So you effectively have two loading models:

eager:
initialize_shaders()
    ↓
load everything

lazy:
get_shader_type()
    ↓
load one

I would choose one.

For your renderer, I think lazy compilation is probably the cleaner architecture:

shader = shader_manager.get(ShaderType.ATOMS)

and:

get()
    → cache hit → return
    → cache miss → compile → cache → return

Then initialization becomes almost unnecessary.

The important exception is if you deliberately want shader compilation during initializeGL() to detect errors before rendering. In that case, keep eager initialization—but then I'd remove the lazy semantics from get_shader_type().

5. The fallback policy is a little too aggressive

Currently:

self.shaders[shader_type] = self.fallback_shader

means the dictionary can contain:

ATOMS   → atoms ShaderProgram
BONDS   → fallback ShaderProgram
SURFACE → surface ShaderProgram

That's convenient, but semantically misleading.

get(ShaderType.BONDS) appears to mean:

"Give me the BONDS shader."

but may actually return:

"Give me the fallback shader because BONDS failed."

I'd rather represent that explicitly.

For example:

@dataclass
class ShaderLoadResult:
    shader: ShaderProgram
    fallback: bool = False

Or simply keep the failed shader absent:

self.shaders[shader_type] = shader

and have:

def resolve(self, shader_type):
    return self.shaders.get(shader_type) or self.fallback_shader

That gives you a much cleaner invariant:

shaders contains only successfully compiled shaders

This becomes particularly useful for diagnostics.

6. _ensure_fallback() is doing something important but should be separated

This method is actually a small FallbackShaderProvider.

The logic:

active shader root
        ↓
src/fallback/
        ↓
PicoGL fallback

is good.

I'd extract it conceptually:

class ShaderFallback:
    def load(...) -> ShaderProgram:
        ...

Then the manager simply does:

except ShaderCompilationError:
    shader = self.fallback.load()

That makes the manager's compilation path much easier to understand.

7. initialize_shaders() is carrying too much state-machine complexity

This is the section I would most strongly refactor.

You have:

_initialized
_initializing
gl_context_available()

plus:

release_shaders()
_initialized = False

plus:

if not self._initialized and not self._initializing:
    self.initialize_shaders()

inside several public methods.

This creates an implicit state machine.

Something like:

CREATED
   │
   ├── no GL context
   │       ↓
   │    CREATED
   │
   └── GL context
           ↓
       INITIALIZING
           ↓
       INITIALIZED
           │
           ↓
       RELEASED

That state machine is real, so I'd make it explicit rather than encode it with two booleans.

For example:

class ShaderManagerState(Enum):
    UNINITIALIZED = auto()
    INITIALIZING = auto()
    READY = auto()
    RELEASED = auto()

Although I would actually go one step further and make the GL context lifecycle external to the manager.

8. The manager shouldn't probably call initialize_shaders() from use_shader_program()

This is subtle but important:

if not self._initialized and not self._initializing:
    self.initialize_shaders()

inside:

use_shader_program()

means that a method called "use this already-existing shader" can suddenly cause compilation of every shader.

That's surprising behavior.

I'd make:

bind(shader)

a very boring operation:

shader.bind()
self.current_shader = shader

No initialization. No loading. No fallback. No policy.

Then:

use_shader_type()

can handle the policy.

That separation makes the API much safer.

9. Uniform handling doesn't belong strongly in ShaderManager

This:

def set_uniform_value(...)

is convenient, but I'd question whether it belongs here.

You already have:

ShaderProgram.set_uniform_name_value()

So this:

shader_manager.set_uniform_value("foo", value)

is effectively shorthand for:

shader_manager.current_shader.set_uniform_name_value("foo", value)

It also introduces implicit state.

I'd prefer:

shader.set_uniform(...)

for general uniforms.

Then the renderer has:

shader = shader_manager.use(ShaderType.ATOMS)
shader.set_uniform(...)

rather than:

shader_manager.use_shader_type(ShaderType.ATOMS)
shader_manager.set_uniform_value(...)

That is a cleaner ownership model.

10. zoom_scale is definitely in the wrong abstraction layer

This is the most obvious example:

if self.current_shader_type == ShaderType.ATOMS:
    loc = gl_get_uniform_location(
        self.current_shader.program,
        "zoom_scale",
    )

The shader manager shouldn't know:

"ATOMS shaders have a zoom_scale uniform."

That's renderer/shader-specific knowledge.

You have already identified this direction in your previous OpenGL refactoring work: the manager should know about programs, not molecular rendering semantics.

I'd move that to something like:

AtomsRenderer.bind_shader(...)

or:

AtomsShader.set_zoom_scale(...)

If you want typed shader interfaces, even better:

class AtomsShader(ShaderProgram):
    def set_zoom_scale(self, value: float) -> None:
        ...

Then:

atoms_shader.set_zoom_scale(zoom_scale)
11. mvp_matrix also probably shouldn't be an argument to use_shader_type()

Currently:

use_shader_type(
    shader_type,
    mvp_matrix=mvp_matrix,
    zoom_scale=zoom_scale,
)

means that shader selection, shader binding, and uniform configuration happen together.

I'd separate:

shader = shader_manager.use(ShaderType.ATOMS)
shader.set_mvp(mvp)
shader.set_zoom_scale(zoom)

Or if MVP is genuinely common to every shader:

shader_manager.bind(ShaderType.ATOMS)
shader_manager.set_mvp(mvp)

But I'd still prefer the first model.

12. The typing needs cleanup

This:

Optional[ShaderProgram | ShaderProgram]

is simply:

ShaderProgram | None

Likewise:

shader_type: str

in load_shader() is wrong given that you subsequently do:

shader_type.value

It should be:

shader_type: ShaderType

And:

mvp_matrix: np.ndarray | glm.mat4 = None

should ideally be:

mvp_matrix: np.ndarray | glm.mat4 | None = None

That matters because this class is becoming infrastructure code, and accurate types become increasingly valuable.

What I would make the public API look like

I'd aim for something approximately this small:

class ShaderManager:
    def __init__(self, shader_directory: Path | None = None):
        self._shaders: dict[ShaderType, ShaderProgram] = {}
        self._fallback: ShaderProgram | None = None
        self._shader_directory = shader_directory
        self._current: ShaderProgram | None = None

    def get(self, shader_type: ShaderType) -> ShaderProgram | None:
        shader = self._shaders.get(shader_type)

        if shader is None:
            shader = self._load(shader_type)

        return shader

    def use(self, shader_type: ShaderType) -> ShaderProgram | None:
        shader = self.get(shader_type)

        if shader is None:
            return None

        shader.bind()
        self._current = shader
        return shader

    def bind(self, shader: ShaderProgram) -> None:
        shader.bind()
        self._current = shader

    def unbind(self) -> None:
        gl_use_program(0)
        self._current = None

    @property
    def current(self) -> ShaderProgram | None:
        return self._current

    def release(self) -> None:
        ...

That's essentially the whole manager.

Then loading becomes an implementation detail:

def _load(self, shader_type: ShaderType) -> ShaderProgram | None:
    ...

And uniform management remains on ShaderProgram.

One architectural change I'd make specifically for your project

Given the OpenGL work you've been doing recently, I'd distinguish these three concepts:

Shader source
     ↓
Shader program
     ↓
Bound shader program

Your current ShaderManager conflates all three.

I'd structure PicoGL roughly as:

ShaderSourceLoader
        │
        ▼
ShaderCompiler
        │
        ▼
ShaderProgram
        │
        ▼
ShaderManager

where:

ShaderSourceLoader
load(shader_type) -> ShaderSource
ShaderCompiler
compile(source) -> ShaderProgram
ShaderProgram

Owns:

program_id
bind()
release()
set_uniform(...)
ShaderManager

Owns:

ShaderType → ShaderProgram
current shader
get()
use()
release()

This would fit very nicely with the broader architecture you've been developing around VertexArrayObject, VBO, ShaderProgram, LayoutDescriptor, etc.

My assessment

I'd give the current implementation 7/10 architecturally.

The important thing is that I don't think it needs a rewrite. The foundations are good.

I'd refactor in this order:

Remove current_shader_program as stored state.
Merge bind() and use_shader_program().
Simplify get_shader_type().
Remove zoom_scale knowledge from the manager.
Move generic uniform operations toward ShaderProgram.
Separate loading/compilation from binding.
Decide firmly between eager and lazy shader compilation.
Make fallback resolution explicit rather than storing fallback under the failed ShaderType.
Only then consider extracting a dedicated ShaderLoader.

The most important conceptual change is:

ShaderManager should manage shader programs; it should not know what those programs mean to the molecular renderer.

That would make it considerably more reusable across your atoms, bonds, surfaces, molecular models, and future renderers—and would also make the modern OpenGL backend much easier to reason about.

---

## Implementation note (refactor applied)

The refactor follows a three-layer model:

1. **Shader source** — `ShaderLoader` / `ShaderFallback` in `picogl/shaders/loader.py`
2. **Shader program** — `ShaderProgram` with `bind()`, `set_uniform()`, `set_mvp()`
3. **Bound program** — `ShaderManager` with `get()`, `resolve()`, `use()`, optional `initialize_shaders()` warm-up

Hybrid compilation: lazy `get()`/`use()` on cache miss; eager `initialize_shaders()` for startup diagnostics. Failed types live in `_failed`; `resolve()` returns the shared fallback without polluting `shaders`. ElMo uploads renderer-specific uniforms via `elmo/gl/shader_bind.py`.