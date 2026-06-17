This is a strong direction—you’re clearly separating binding strategy (VAO vs client state) from pipeline semantics (legacy vs shader). That’s exactly the right axis of abstraction.
But right now you have a conceptual mismatch between three layers:
Binding (mesh → GPU state)
Pipeline (how vertices are interpreted / transformed)
Draw execution (issuing draw calls)
They’re partially separated—but not cleanly composed yet.
Let’s tighten this into something that scales into your render graph + backend.
1) Immediate issues in your current design
❌ GLPipeline is mixing abstraction levels
This protocol:
class GLPipeline(Protocol):
    def set_projection(...)
    def translate(...)
    def set_light(...)
    def vertex_3f(...)
is pure fixed-function thinking.
But your system also has:
Modern VAO binding
Shader-based rendering
👉 These APIs are fundamentally incompatible.
Problem:
You’re trying to unify:
Immediate mode (glVertex3f)
Fixed pipeline transforms
Modern shader pipeline
into one interface.
That interface will collapse under complexity.
❌ GLBindingStrategy is underpowered
class GLBindingStrategy(ABC):
    def bind_mesh(self, mesh): ...
    def draw(self, mesh, mode): ...
This is missing a critical concept:
Binding is not enough—you need a draw submission unit
Right now:
binding + draw are loosely coupled
no notion of “prepared GPU object”
❌ LegacyBinding bug
glEnableClientState(GLClientState.COLOR)
glTexCoordPointer(...)
This is incorrect:
glEnableClientState(GLClientState.TEXTURE_COORD_ARRAY)
2) The real abstraction you want
You should converge toward three clean layers:
Layer 1 — Geometry (CPU-side)
@dataclass
class MeshData:
    vertices: np.ndarray
    normals: Optional[np.ndarray]
    colors: Optional[np.ndarray]
    texcoords: Optional[np.ndarray]
    indices: Optional[np.ndarray]
Layer 2 — GPU representation (binding result)
class GPUMesh(ABC):
    @abstractmethod
    def bind(self): ...

    @abstractmethod
    def draw(self, mode): ...
Layer 3 — Pipeline (how it is rendered)
class Pipeline(ABC):
    @abstractmethod
    def bind(self): ...
3) Refactor your BindingStrategy into a factory
Instead of:
binding.bind_mesh(mesh)
binding.draw(mesh)
You want:
binding produces a GPU object
Refactored design
class GLBindingStrategy(ABC):
    @abstractmethod
    def upload(self, mesh: MeshData) -> "GPUMesh":
        ...
Legacy implementation
class LegacyMesh(GPUMesh):
    def __init__(self, mesh):
        self.mesh = mesh

    def bind(self):
        if self.mesh.vertices is not None:
            glEnableClientState(GL_VERTEX_ARRAY)
            glVertexPointer(3, GL_FLOAT, 0, self.mesh.vertices)

        if self.mesh.normals is not None:
            glEnableClientState(GL_NORMAL_ARRAY)
            glNormalPointer(GL_FLOAT, 0, self.mesh.normals)

    def draw(self, mode):
        if self.mesh.indices is not None:
            glDrawElements(mode, len(self.mesh.indices), GL_UNSIGNED_INT, self.mesh.indices)
Modern implementation
class ModernMesh(GPUMesh):
    def __init__(self, vao, index_count):
        self.vao = vao
        self.index_count = index_count

    def bind(self):
        glBindVertexArray(self.vao)

    def draw(self, mode):
        glDrawElements(mode, self.index_count, GL_UNSIGNED_INT, None)
Binding strategies now create these
class LegacyBinding(GLBindingStrategy):
    def upload(self, mesh: MeshData) -> GPUMesh:
        return LegacyMesh(mesh)


class ModernBinding(GLBindingStrategy):
    def upload(self, mesh: MeshData) -> GPUMesh:
        vao = create_vao(mesh)
        return ModernMesh(vao, len(mesh.indices))
4) Replace GLPipeline with two explicit pipelines
Instead of one giant Protocol, split:
Legacy pipeline (fixed-function)
class LegacyPipeline:
    def apply_state(self, state: RenderState):
        # glMatrixMode, glLight, etc.
Modern pipeline (shader-based)
class ShaderPipeline:
    def __init__(self, program):
        self.program = program

    def bind(self):
        glUseProgram(self.program)

    def set_uniforms(self, state: RenderState):
        ...
Key insight
Pipeline != Binding
Concept	Responsibility
Binding	Geometry → GPU buffers
Pipeline	How GPU interprets data
Backend	State + orchestration
5) Integrate into your render graph system
Now a RenderPass becomes:
@dataclass
class RenderPass:
    state: RenderState
    pipeline: Pipeline
    mesh: GPUMesh
    mode: int

    def execute(self, backend):
        backend.apply_state(self.state)
        self.pipeline.bind()
        self.mesh.bind()
        self.mesh.draw(self.mode)
6) Why this is a major improvement
✔ Eliminates API confusion
No more:
vertex_3f()
set_projection()
✔ Works for both legacy and modern GL
LegacyMesh + LegacyPipeline
ModernMesh + ShaderPipeline
✔ Aligns with your backend architecture
Backend handles state
Pipeline handles shader/fixed logic
Mesh handles geometry
✔ Enables caching
You can now:
gpu_mesh = binding.upload(mesh_data)
and reuse it across frames.
7) Where your current design was heading (but not quite landing)
You were implicitly trying to build:
A unified rendering abstraction across GL paradigms
But the correct way is not to unify APIs—it’s to separate responsibilities cleanly.
8) Final architectural snapshot
After refactor:
RenderGraph
  ↓
RenderPass
  ├── RenderState
  ├── Pipeline (shader or legacy)
  └── GPUMesh (VAO or client arrays)
        ↓
GLBackend (state diffing)
        ↓
GL Drivers (raster, depth, blend)
9) Blunt conclusion
You’re very close, but:
❌ GLPipeline should not exist in its current form
❌ BindingStrategy should produce objects, not act immediately
❌ Immediate-mode style APIs need to be isolated, not unified
✅ You already have the right instincts (separation of concerns)
✅ You’re one refactor away from a clean, engine-grade abstraction
If you want next step, I can extend this into:
→ full shader system + uniform binding + material system
(which plugs directly into your RenderState and eliminates most manual uniform calls)