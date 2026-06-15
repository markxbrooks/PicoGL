ou already are using composition—but it’s inconsistent and stops at the “driver” layer. Right now GLBackend is doing three conflicting jobs:

Facade (good): delegating to binding, raster, legacy
God object (problem): owns dozens of raw GL calls
State executor (partially duplicated with RenderStateApplier)

That tension is exactly where deeper composition helps.

The Core Problem

Your backend still exposes raw OpenGL verbs everywhere:

glEnable(...)
glDisable(...)
glVertexPointer(...)
glTexCoordPointer(...)

That means:

No real abstraction boundary
No swappability (modern vs legacy still leaks everywhere)
State logic is split between:
GLBackend
RenderStateApplier
GLStateManager (from your file)
What “More Composition” Actually Means Here

You want to invert GLBackend into a coordinator of subsystems, not a container of functions.

Instead of:

self.raster = GLRasterDriver()
self.legacy = GLLegacyPipeline()

You push further into orthogonal, replaceable domains:

1. Introduce a Capability/State Subsystem (You already started this)

You already have:

GLStateManager
RenderStateApplier

But GLBackend still bypasses them:

def set_depth_test(enabled):
    glEnable(GL_DEPTH_TEST) if enabled else glDisable(GL_DEPTH_TEST)
Fix: Fully delegate state
class GLBackend:
    def __init__(self, ...):
        self.state = GLStateManager(self)
        self.state_applier = RenderStateApplier(self)

Then remove:

set_depth_test
set_blend
set_cull_face
set_lighting
enable/disable

Replace with:

self.state.set_enabled(GL_DEPTH_TEST, True)

Now:

All capability transitions are centralized
Redundant state changes disappear
Backend becomes stateless executor
2. Split Fixed-Function vs Modern into Strategy Objects

Right now:

self.legacy = GLLegacyPipeline()

But GLBackend still exposes:

glMatrixMode
glLoadIdentity
glColor4f
glVertex3f
Instead: full pipeline composition
class GLPipeline(Protocol):
    def set_projection(...)
    def apply_transform(...)
    def set_material(...)
    def draw_mesh(...)

Then:

self.pipeline: GLPipeline = LegacyPipeline()  # or ModernPipeline

Now remove ALL of these from GLBackend:

set_matrix_mode_*
load_identity
translate
set_light_position
set_material
immediate mode calls (vertex_3f, etc.)

Those belong to the pipeline strategy, not the backend.

3. Extract a Geometry Submission Layer

You currently mix:

binding.bind_mesh
raw glDrawElements
client state (glVertexPointer)
Create:
class GeometryDriver:
    def bind(self, mesh): ...
    def draw(self, mesh, mode): ...

Then:

self.geometry = GeometryDriver(binding)

And replace:

def draw_mesh(self, mesh, mode):
    self.binding.bind_mesh(mesh)
    self.binding.draw(mesh, gl_value(mode))

with:

self.geometry.draw(mesh, mode)

Now binding is no longer leaked into backend API.

4. Extract Texture System (big win)

Right now:

@staticmethod
def create_texture(...)

This is a red flag—resource lifecycle inside backend.

Move to:
class TextureSystem:
    def create(self, spec, data) -> Texture
    def bind(self, texture)
    def delete(self, texture)

Then:

self.textures = TextureSystem(GLTextureDriver())

Now backend no longer knows:

how textures are created
how they’re initialized
5. Extract Legacy Client-State (this is currently the messiest part)

All of this:

enable_vertex_array
glVertexPointer
glNormalPointer
glColorPointer

→ should live in something like:

class LegacyAttributeBinder:
    def bind(mesh)

You already almost have this:

GLAttributeArray.enable_legacy()

So finish it:

Remove all client-state functions from GLBackend
Let mesh/attribute system handle it
6. Clip Planes → State Object Only

You already have:

GLClipPlaneState.apply(state)

But GLBackend still has:

enable_clip_plane0()
disable_clip_plane0()

Delete those.

Use:

clip_state.apply(self.state)
7. Reduce GLBackend to a Thin Orchestrator

After decomposition, GLBackend should look closer to:

class GLBackend:
    def __init__(self, pipeline, geometry, textures):
        self.pipeline = pipeline
        self.geometry = geometry
        self.textures = textures
        self.state = GLStateManager(self)
        self.state_applier = RenderStateApplier(self)

    def apply_state(self, state: RenderState):
        self.state_applier.apply(state)

    def draw(self, command: DrawCommand):
        command.execute(self)

That’s it.

Everything else is delegated.

8. What You Gain
Before
Backend = 70+ methods
Mixed abstraction levels
Hard to swap legacy/modern
State logic duplicated
After
Backend = orchestrator only
Systems:
StateManager
Pipeline
GeometryDriver
TextureSystem
Clean boundaries
True backend interchangeability
The Key Insight

You don’t want:

“GLBackend with composed helpers”

You want:

“A rendering system composed of subsystems, with GLBackend as the wiring layer”

If You Want the Next Step

The natural evolution from here (and what your current design is very close to) is:

Frame graph / render graph
Resource registry (textures, buffers, FBOs)
Stateless command submission

Which eliminates almost all manual orchestration.

If you want, I can take your current code and show a 
minimal frame graph built on top of this design—that’s the point where PicoGL-style architecture really clicks.