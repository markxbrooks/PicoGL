Yes. There is quite a bit of duplication, and I think the module could be reduced by around 30–40% without losing readability. There are also a couple of bugs that have probably crept in because of the duplication.

The main areas I noticed are:

1. Validation logic is repeated three times ⭐⭐⭐

render_isosurface_mesh_data(), render_isosurface_safe(), and render_isosurface_mesh() all perform essentially the same validation:

null checks
empty array checks
contiguous conversion
NaN/Inf validation
index validation
mesh size limits

For example:

if np.any(np.isnan(vertices)) or np.any(np.isinf(vertices)):
    ...

appears repeatedly.

Likewise:

if np.any(faces < 0) or np.any(faces >= vertex_count):

and

if len(vertices) > MAX_VERTEX_COUNT:
I'd extract
def validate_mesh(vertices, indices):
    ...
    return vertices, indices, vertex_count

or

MeshValidationResult(
    vertices,
    indices,
    vertex_count,
)

Then every renderer becomes

vertices, faces, vertex_count = validate_mesh(vertices, faces)
2. Drawing logic is duplicated ⭐⭐⭐⭐

You already started extracting this into

_draw_surface(...)

but render_isosurface_mesh_data() still has almost identical code.

Specifically:

with legacy_client_states(...):
    ...
    gl_backend.geometry.draw_elements(...)

is almost the same.

I'd probably make _draw_surface() more generic:

_draw_surface(
    vertices,
    indices,
    normals=None,
    colors=None,
    fill_mode=False,
    line_width=1.0,
)

Then all three public renderers reduce to

validate
↓

prepare optional arrays

↓

_draw_surface(...)
3. Backend setup repeated

This appears several times

gl_backend = _resolve_backend(backend)

gl_backend.depth.set_depth_test(True)
gl_backend.raster.set_line_width(line_width)

That could become

_setup_backend(
    backend,
    line_width,
    rgba_color,
)
4. Polygon mode restore

This appears repeatedly

gl_backend.raster.set_polygon_mode(
    GLFace.FRONT_AND_BACK,
    GLFillMode.FILL
)

I'd actually make a context manager

with polygon_mode(GLFillMode.LINE):
    draw()

Then restoring is automatic.

5. Exception handling duplicated

Every renderer ends with

except Exception as ex:
    log.error(...)
    import traceback
    traceback.print_exc()

Likewise

try:
    gl_backend.geometry.draw_elements(...)
except Exception as draw_error:

appears repeatedly.

6. Logging duplicated

These are almost identical

Rendered isosurface with ...

vs

Safely rendered isosurface with ...

I'd centralize into

_log_render(vertex_count, face_count)
7. Contiguous conversion

You have

vertices = np_contiguous_array(vertices)
faces = np_contiguous_array(faces, dtype=np.uint32)

multiple times.

8. Client-state setup

You have

with legacy_client_states(GLClientState.VERTEX):

and

with legacy_client_states(
    GLClientState.VERTEX,
    *(GLClientState.NORMAL,) * has_normals,
    *(GLClientState.COLOR,) * True,
):

These are really the same operation.

A helper like

_draw_arrays(
    vertices,
    normals=None,
    colors=None,
)

would eliminate this duplication.

There are also two bugs
Bug #1

Your helper

def np_contiguous_array(mesh_data: np.ndarray, dtype=np.float32):
    return np.ascontiguousarray(mesh_data.colors, dtype=dtype)

This is almost certainly wrong.

It always returns

mesh_data.colors

instead of the object passed in.

It should probably be

def np_contiguous_array(array, dtype=np.float32):
    return np.ascontiguousarray(array, dtype=dtype)

Otherwise this line

vertices = np_contiguous_array(vertices)

will fail because vertices is a NumPy array and has no .colors attribute.

Bug #2

In render_isosurface_mesh_data()

color_data = np_contiguous_array(mesh_data)

Because of the helper bug above, this currently works only by accident—it extracts mesh_data.colors indirectly. If you fix np_contiguous_array(), you'll need to update this to:

color_data = np_contiguous_array(mesh_data.colors)

which is much clearer.

Overall structure

I would simplify the module to something like:

validate_mesh()

_prepare_mesh_data()

_setup_backend()

_draw_surface()

render_isosurface_mesh()

render_isosurface_mesh_data()

render_isosurface_safe()

Each public renderer should be only about 15–25 lines, with almost all of the OpenGL mechanics encapsulated in shared helpers.

Overall, I'd rate the duplication as:

Area	Duplication
Validation	★★★★★
Drawing	★★★★☆
Backend setup	★★★☆☆
Exception handling	★★★☆☆
Logging	★★☆☆☆

The module already shows signs of being refactored (for example, _draw_surface() and _resolve_backend()), but it looks like the refactoring stopped halfway. Finishing that process would make the code noticeably smaller, easier to maintain, and less prone to inconsistencies like the np_contiguous_array() bug.