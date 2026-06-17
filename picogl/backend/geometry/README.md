# Geometry / Binding / Pipeline — draw call inventory

Phase 0 inventory for the binding/pipeline refactor ([`raster.md`](../GL/driver/raster.md)).
Documents **where drawing actually happens today** before introducing `GPUMesh` and split pipelines.

## Three layers (target)

| Layer | Responsibility | Today |
|-------|----------------|---------|
| **Geometry (CPU)** | `MeshData`, entity mesh builders | `picogl/renderer/meshdata.py`, ElMo entity buffers |
| **GPU representation** | Upload once, bind + draw | Entity VAOs, `GLMesh`, `DrawableBuffer` — no unified `GPUMesh` yet |
| **Pipeline** | How vertices are interpreted | Split in practice; unified only on paper via `GLPipeline` |

## PicoGL binding (`GLBindingStrategy`)

**Definition:** [`picogl/backend/geometry/factory.py`](factory.py) (re-exported from [`opengl.py`](../opengl.py))

| Class | Role | Production usage |
|-------|------|------------------|
| `LegacyBinding` | `upload()` → `LegacyMesh`; deprecated `bind_mesh`/`draw` shims | Widget/renderer construction only |
| `ModernBinding` | `upload()` → `ModernMesh` (VAO via `GLMesh`) | Widget/renderer construction only |
| `GPUMesh` | `bind()` / `draw(mode)` / `delete()` | New API; use via `upload()` or `DrawableBufferAdapter` |
| `GLGeometryDriver.draw_gpu_mesh` | Bind + draw + unbind a `GPUMesh` | New API |

Phase 1 added [`picogl/backend/geometry/`](.) — see `mesh.py`, `legacy_mesh.py`, `modern_mesh.py`, `factory.py`, `adapter.py`. Tests: `test_binding.py`, `test_geometry_binding.py`.

### Fixed in Phase 0

`LegacyBinding.bind_mesh` incorrectly enabled `GL_COLOR_ARRAY` when binding texture coordinates. Correct state is `GLClientState.TEXCOORD` (`GL_TEXTURE_COORD_ARRAY`). Regression: `picogl/tests/test_binding.py`.

## Pipeline (split legacy vs shader)

| Type | Location | Role |
|------|----------|------|
| `LegacyPipeline` (`GLLegacyPipeline`) | [`legacy/core/pipeline.py`](../legacy/core/pipeline.py) | Fixed-function matrices, lights, materials, immediate-mode helpers |
| `ShaderPipeline` | [`modern/core/pipeline/shader_pipeline.py`](../modern/core/pipeline/shader_pipeline.py) | `glUseProgram` + uniform upload |
| `GLBackend.legacy` | [`GL/backend.py`](../GL/backend.py) | Fixed-function pipeline entry |
| `GLBackend.shader` | same | Default modern pipeline slot |
| `GLBackend.pipeline` | same | **Deprecated** alias for `.legacy` |

`GLPipeline` protocol in [`opengl.py`](../opengl.py) is deprecated — use `LegacyPipeline` or `ShaderPipeline` explicitly. Modern rendering does not implement the old unified protocol.

Phase 2 split pipelines **(done)**. Tests: `test_shader_pipeline.py`.

## ElMo draw paths (production)

### A. Binding construction (init only)

| File | Binding |
|------|---------|
| `elmo/ui/widgets/gl/renderer/legacy.py` | `LegacyBinding()` |
| `elmo/ui/widgets/gl/mol/modern.py` | `ModernBinding()` |
| `elmo/gl/backend/legacy/entities/isosurface/mesh.py` | `LegacyBinding()` (fallback backend) |
| `elmo/gl/backend/modern/entities/isosurface/renderer.py` | `ModernBinding()` (fallback backend) |
| `picogl/ui/backend/glut/window/glut_legacy.py` | `LegacyBinding()` |

### B. Legacy immediate-mode pipeline

`backend.legacy.set_color`, `tex_coord2f`, `vertex_3f` — textured triangle strips without VAO:

- `elmo/ui/widgets/gl/renderer/legacy.py` (cube per-face textured draw)
- `elmo/ui/widgets/gl/mol/legacy.py` (`load_identity`, matrix mode)
- `elmo/gl/backend/legacy/entities/isosurface/mesh.py` (`set_color`)
- `elmo/gl/backend/legacy/entities/highlighted_atom/draw.py` (`set_color`)

Static `GLLegacyPipeline.set_color` (bypasses `backend.legacy`):

- `elmo/gl/backend/legacy/entities/bond/buffer.py`
- `elmo/gl/backend/legacy/entities/water/draw.py`
- `elmo/gl/backend/legacy/gizmos/axes/renderer.py`

### C. Entity VAO / `DrawableBuffer` `.draw()` (primary modern + legacy path)

Entity arrays and VAOs implement [`DrawableBuffer`](../../protocols/drawable_buffer.py) (`bind` / `draw` / `delete`):

- Modern: `AtomVAO`, `BondsVAO`, `RibbonVAO`, `CalphasVAO`, highlighted atom VAO, unit cell `GLMesh`
- Legacy: ribbon `VertexBufferGroup`, bond EBO, calpha VBO, axes VBG, unit cell mesh

Representative call sites: `elmo/gl/backend/modern/entities/**/draw.py`, `elmo/gl/backend/legacy/**`.

### D. Static geometry driver helpers (bypass binding strategy)

`GLGeometryDriver.draw_elements`, `draw_bound_elements`, `draw_arrays`, `draw_arrays_bound_vao`:

- Legacy isosurface mesh fallbacks (`isosurface/mesh.py`)
- Modern highlighted atom pick draw (`highlighted_atom/draw.py`)
- Legacy bond buffer (`bond/buffer.py`)

### E. Declarative state + render graph (newer path)

- `backend.apply_state(RenderState)` — frame setup, surface `submit()` (`elmo/ui/widgets/gl/mol/modern.py`, `renderer/modern.py`)
- `RenderGraphExecutor` — experimental `render_test()` for isosurface + cube passes
- Passes build `RenderContext.state`: cube, isosurface, Connolly (`elmo/ui/widgets/gl/renderer/passes/`)

Shaders and uniforms remain **outside** `RenderState` (manual `shader_state()`, `ShaderManager`).

## Dead or rarely used paths

| API | Status |
|-----|--------|
| `GLBindingStrategy.bind_mesh` / `draw` per frame | Constructed on backend; ElMo entities don't call through geometry driver |
| `backend.geometry.draw_mesh` | Tests + `DrawCommand` only |
| `MeshData.draw()` | Legacy fallbacks avoid it (isosurface comments) |
| `GLPipeline` protocol | Deprecated; legacy-only alias |

## Correct reference implementations for client-state binding

When implementing `LegacyMesh` (Phase 1), align with:

- [`LegacyAttributeBinder`](../legacy/core/attribute_binder.py) — `enable_texcoord_array()` uses `GL_TEXTURE_COORD_ARRAY`
- [`MeshData.bind()`](../../renderer/meshdata.py) — same client-state pattern
- [`LegacyBinding`](../opengl.py) — after Phase 0 fix

## Next phases (summary)

1. **Phase 1** — `picogl/backend/geometry/`: `GPUMesh`, `upload()` factory, `DrawableBufferAdapter` **(done)**
2. **Phase 2** — Split `LegacyPipeline` vs `ShaderPipeline`; deprecate `GLPipeline` **(done)**
3. **Phase 3** — Structured `RenderPass` (`pipeline` + `gpu_mesh` + `mode`)
4. **Phase 4** — ElMo pilot migrations (adapter + structured passes)
5. **Phase 5** — Remove shims and duplicate bind logic
