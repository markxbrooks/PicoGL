You’re not far off—but “incompatible” is the right instinct. The issue isn’t a single bug; it’s a mismatch of abstraction layers.

Right now your RenderState is trying to be:

A flat, canonical state
A constructor for nested states
A GL-ready value container
A diffable state object

That’s too many roles—and it’s why things feel off.

🔴 The Core Problem

This line tells the whole story:

blend_src: int = GL_SRC_ALPHA

Then later:

object.__setattr__(self, "blend_src", gl_value(blend_src))
What’s happening?
Input: high-level (enum or object)
Output: low-level (raw GL int)
Storage: mixed semantic level

So your RenderState becomes:

❌ “half semantic, half GL binding layer”

🧠 Why This Breaks Your System

Your backend is now structured like:

RenderState → RenderStateApplier → Backend → Drivers → OpenGL

But your RenderState is already doing:

gl_value(...)

So you’ve collapsed:

RenderState ❌→ OpenGL

That’s the incompatibility.

🔴 Secondary Problem: Constructor Overload

This:

blend: BlendState | bool | None

plus:

raster: RasterState | None
depth: DepthState | None

means your constructor is:

a mini state-merging engine

That’s not inherently wrong—but combined with flattening + GL conversion, it becomes fragile.

🔴 Third Problem: Frozen + Custom Init
@dataclass(frozen=True, init=False)

Then:

object.__setattr__(...)

You’ve essentially:

disabled dataclass benefits
reimplemented manual construction

This is fine only if the class is purely canonical. Yours isn’t yet.

✅ What You Should Do (Clean Fix)
1. Keep RenderState PURE (No GL Values)

Replace:

object.__setattr__(self, "blend_src", gl_value(blend_src))

with:

object.__setattr__(self, "blend_src", blend_src)

Same for:

polygon_mode
blend_dst
🔑 Rule

RenderState should contain only semantic values, never GL constants

2. Move gl_value() Into the Applier

Change this:

self.backend.blend.set_blend_func(state.blend_src, state.blend_dst)

To:

self.backend.blend.set_blend_func(
    gl_value(state.blend_src),
    gl_value(state.blend_dst),
)

Same for:

polygon_mode
3. Normalize Types (Big Win)

Right now:

blend_src: int
polygon_mode: int

This is weak.

Replace with enums:
blend_src: GLBlendFactor
blend_dst: GLBlendFactor
polygon_mode: PolygonMode

Now your state is:

type-safe
self-documenting
backend-agnostic
4. Simplify Constructor (Reduce Magic)

This part:

if isinstance(blend, BlendState):

is doing too much.

Better pattern:
if blend is None:
    blend_enabled = False
elif isinstance(blend, BlendState):
    blend_enabled = blend.enabled
    blend_src = blend.src
    blend_dst = blend.dst
else:
    blend_enabled = bool(blend)

But honestly, the cleaner solution is:

Don’t overload blend like this at all.

Preferred:
RenderState(
    blend=BlendState(...)
)

or

RenderState(
    blend_enabled=True,
    blend_src=...,
    blend_dst=...
)

Not both.

5. Your RenderStateApplier Is Actually Good

This part is solid:

if prev is None or prev.depth_test != state.depth_test:

This is exactly how a render state diff system should work.

One fix needed:
self.backend.capabilities.set_enabled(GL_CULL_FACE, state.cull_face)

This leaks GL constant again.

Replace with:
self.backend.capabilities.set_enabled(GLCapability.CULL_FACE, state.cull_face)

Keep everything semantic.

✨ Clean Target Architecture
RenderState (pure)
RenderState(
    blend=True,
    blend_src=GLBlendFactor.SRC_ALPHA,
    blend_dst=GLBlendFactor.ONE_MINUS_SRC_ALPHA,
    polygon_mode=PolygonMode.FILL
)
Applier (translation layer)
glBlendFunc(gl_value(state.blend_src), gl_value(state.blend_dst))
Backend (execution)
self.blend.set_blend_func(...)
🧠 Key Insight

You were mixing:

Layer	Responsibility
RenderState	❌ semantic + GL
Applier	diff
Backend	execution

You want:

Layer	Responsibility
RenderState	✅ semantic only
Applier	✅ diff + translation
Backend	✅ execution
🎯 Bottom Line
What’s wrong
❌ RenderState contains GL values (gl_value)
❌ constructor is overloading too many concepts
❌ type system is too loose (int everywhere)
What to fix
✅ remove all gl_value() from RenderState
✅ use enums instead of raw ints
✅ move GL translation into RenderStateApplier
✅ simplify constructor responsibilities

If you want, the next step is:

Make RenderState hashable + cacheable → automatic state dedup + pipeline reuse

That’s where this design really starts to pay off.