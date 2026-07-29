# class BufferFactory(BufferFactoryBase):

The main issue is that you're repeating the same pattern for every drawable:

Validate the data.
Create the VAO.
Add a series of VBOs.
Add an optional EBO.
Assign a layout.

The differences are only:

the VAO class (RibbonVAO, BondsVAO, ...)
which VBOs exist
the attribute order
whether there is an EBO

That suggests moving toward a generic VAO builder.

1. Create a generic VAO construction helper

Instead of every setup_* function manually calling add_vbo, write one helper.

from dataclasses import dataclass

@dataclass(frozen=True)
class VertexAttribute:
    index: int
    data: np.ndarray
    name: VBOType


def build_vao(
    vao: VertexArrayObject,
    attributes: list[VertexAttribute],
    indices: np.ndarray | None = None,
) -> VertexArrayObject:
    """Populate a VAO from a list of vertex attributes."""

    for attribute in attributes:
        vao.add_vbo(
            index=attribute.index,
            data=attribute.data,
            size=attribute.data.shape[1],
            name=attribute.name,
        )

    if indices is not None:
        vao.add_ebo(indices)

    return vao

Then your ribbon setup becomes almost trivial.

def setup_ribbon_vao(
    colors,
    indices,
    normals,
    positions,
) -> RibbonVAO:

    positions = as_vec3_array(positions)
    normals = as_vec3_array(normals)
    colors = as_vec3_array(colors)
    indices = np.asarray(indices, dtype=np.uint32).reshape(-1)

    return build_vao(
        RibbonVAO(),
        [
            VertexAttribute(0, positions, VBOType.VBO),
            VertexAttribute(1, normals, VBOType.NBO),
            VertexAttribute(2, colors, VBOType.CBO),
        ],
        indices,
    )

Likewise bonds:

def setup_bond_buffers(
    indices,
    colors,
    normals,
    positions,
) -> BondsVAO:

    return build_vao(
        BondsVAO(),
        [
            VertexAttribute(0, positions, VBOType.VBO),
            VertexAttribute(1, colors, VBOType.CBO),
            VertexAttribute(2, normals, VBOType.NBO),
        ],
        indices,
    )

Now there is almost no duplicated OpenGL code.

2. Eliminate the setup_bond_vbg() wrappers

These methods

setup_atom_vbg()
setup_bond_vbg()
setup_calpha_vbg()

don't actually add any value—they simply forward arguments.

For example

def setup_bond_vbg(...):
    return setup_bond_buffers(...)

exists only so _try_setup() can call a bound method.

Instead, _try_setup() can directly call the module function.

bond_vao = self._try_setup(
    setup_bond_buffers,
    bond_indices_flat,
    colors,
    normals,
    positions,
)

Then remove

setup_bond_vbg()
setup_atom_vbg()
setup_calpha_vbg()

entirely.

That removes six nearly identical methods from the class.

3. Generalize the "validate + build + layout" pattern

These methods

setup_atom_buffers()
setup_bond_buffers()
setup_calpha_buffers()

are almost identical.

You can factor them into one helper.

def _build_buffer(
    self,
    *,
    layout,
    setup_func,
    validator=None,
    **kwargs,
):
    if validator:
        validator(**kwargs)

    vao = self._try_setup(setup_func, **kwargs)

    if vao:
        vao.set_layout(layout)

    return vao

Then atoms become

def setup_atom_buffers(self, colors, normals, positions):

    return self._build_buffer(
        layout=setup_atom_layout(),
        setup_func=setup_atom_buffers,
        validator=lambda **k: validate_input_data(
            colors=k["colors"],
            normals=k["normals"],
            vertices=k["positions"],
        ),
        colors=colors,
        normals=normals,
        positions=positions,
    )

Bonds become

def setup_bond_buffers(
    self,
    bond_indices_flat,
    colors,
    normals,
    positions,
):

    return self._build_buffer(
        layout=setup_bond_layout(),
        setup_func=setup_bond_buffers,
        validator=lambda **k: validate_input_data(
            colors=k["colors"],
            normals=k["normals"],
            vertices=k["positions"],
        ),
        indices=bond_indices_flat,
        colors=colors,
        normals=normals,
        positions=positions,
    )

Now every drawable is only describing what it needs instead of how to build it.

4. Consider moving layouts into the setup functions

Currently the factory knows both

how to construct a VAO
which layout belongs to it

That coupling means every new drawable requires changes in two places.

Instead:

setup_bond_vao(...)

could do

vao = build_vao(...)
vao.set_layout(setup_bond_layout())
return vao

Then the factory simply becomes

return self._try_setup(
    setup_bond_vao,
    ...
)

The factory no longer knows anything about attribute layouts.

5. Introduce a reusable attribute specification

If you're creating many drawables (atoms, bonds, ribbons, spheres, cylinders, meshes), you can make the setup almost declarative.

ATTRIBUTE_POSITION = VertexAttributeSpec(0, VBOType.VBO)
ATTRIBUTE_NORMAL  = VertexAttributeSpec(1, VBOType.NBO)
ATTRIBUTE_COLOR   = VertexAttributeSpec(2, VBOType.CBO)

Then

build_vao(
    RibbonVAO(),
    [
        ATTRIBUTE_POSITION.with_data(positions),
        ATTRIBUTE_NORMAL.with_data(normals),
        ATTRIBUTE_COLOR.with_data(colors),
    ],
    indices,
)

The attribute ordering becomes standardized across your renderer, reducing the risk of mismatched layouts.

Overall recommendation

Your current design is already reasonably modular. The biggest improvements would come from:

Introducing a generic build_vao() helper to eliminate repeated add_vbo()/add_ebo() code.
Removing the setup_*_vbg() pass-through methods.
Factoring the repeated "validate → build → set layout" workflow into a single private helper.
Moving layout assignment closer to VAO construction so the factory only orchestrates object creation.

These changes would reduce the amount of boilerplate significantly while making it easier to add new drawable types such as surfaces, cylinders, cartoons, and instanced geometry with minimal additional code.