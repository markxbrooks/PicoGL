#!/usr/bin/env python3
import os
import shutil
import argparse
import re
from pathlib import Path

# -----------------------------

# CONFIG: FILE MOVE MAP

# -----------------------------

MOVE_MAP = {
# --- CORE ---
"backend/modern/core/mvp.py": "core/math/mvp.py",
"backend/modern/core/unproject.py": "core/math/unproject.py",
"backend/legacy/core/camera/unproject.py": "core/math/unproject_legacy.py",

```
"mode.py": "core/enums/mode.py",
"state/draw_mode.py": "core/enums/draw_mode.py",

"error.py": "core/errors/gl_errors.py",

# --- gl BACKEND ---
"backend/gl/driver/blend.py": "backend/gl/driver/blend.py",
"backend/gl/driver/capability.py": "backend/gl/driver/capability.py",
"backend/gl/driver/depth.py": "backend/gl/driver/depth.py",
"backend/gl/driver/frame.py": "backend/gl/driver/frame.py",
"backend/gl/driver/geometry.py": "backend/gl/driver/geometry.py",
"backend/gl/driver/raster.py": "backend/gl/driver/raster.py",
"backend/gl/driver/framebuffer.py": "backend/gl/driver/framebuffer.py",

# --- WRAPPERS ---
"wrappers/buffer.py": "backend/gl/wrappers/buffer.py",
"wrappers/draw.py": "backend/gl/wrappers/draw.py",
"wrappers/vertex_array.py": "backend/gl/wrappers/vao.py",
"wrappers/vertex_attrib_pointer.py": "backend/gl/wrappers/attrib.py",
"wrappers/enable_vertex_array.py": "backend/gl/wrappers/enable.py",

# --- STATE ---
"state/query.py": "backend/state/query.py",
"state/param.py": "backend/state/param.py",

# --- MODERN VERTEX ---
"backend/modern/core/vertex/base.py": "backend/modern/vertex/base.py",
"backend/modern/core/vertex/buffer/object.py": "backend/modern/vertex/vbo.py",
"backend/modern/core/vertex/buffer/element.py": "backend/modern/vertex/ebo.py",
"backend/modern/core/vertex/array/helpers.py": "backend/modern/vertex/helpers.py",

# --- BUFFERS → GPU ---
"buffers/attributes.py": "gpu/buffers/layout.py",
"buffers/base.py": "gpu/buffers/base.py",
"buffers/vertex/vbo/vbo_class.py": "gpu/buffers/vbo_types.py",
"buffers/vertex/aliases.py": "gpu/buffers/aliases.py",
"buffers/glcleanup.py": "gpu/buffers/cleanup.py",

# --- FRAMEBUFFER ---
"buffers/glframe.py": "gpu/framebuffer.py",
"renderer/readback.py": "gpu/readback.py",

# --- RENDERER ---
"renderer.py": "renderer/mesh.py",
"frame.py": "renderer/frame.py",

# --- INIT ---
"utils/gl_init.py": "backend/init/tasks.py",
```

}

# -----------------------------

# IMPORT REWRITE RULES

# -----------------------------

REWRITE_RULES = [
(r"picogl.backend.gl.", "picogl.backend.gl."),
(r"picogl.mode", "picogl.core.enums.mode"),
(r"picogl.error", "picogl.core.errors.gl_errors"),
(r"picogl.state.draw_mode", "picogl.core.enums.draw_mode"),
(r"picogl.wrappers.", "picogl.backend.gl.wrappers."),
(r"picogl.buffers.", "picogl.gpu.buffers."),
]

# -----------------------------

# UTILITIES

# -----------------------------

def ensure_dir(path: Path):
path.parent.mkdir(parents=True, exist_ok=True)

def move_file(src_root: Path, dst_root: Path, src_rel: str, dst_rel: str, dry_run=True):
src = src_root / src_rel
dst = src_root / dst_rel

```
if not src.exists():
    print(f"[WARN] Missing: {src_rel}")
    return

ensure_dir(dst)

print(f"[MOVE] {src_rel} → {dst_rel}")
if not dry_run:
    shutil.move(str(src), str(dst))
```

def rewrite_imports(root: Path, dry_run=True):
for py_file in root.rglob("*.py"):
with open(py_file, "r", encoding="utf-8") as f:
content = f.read()

```
    new_content = content
    for pattern, replacement in REWRITE_RULES:
        new_content = re.sub(pattern, replacement, new_content)

    if new_content != content:
        print(f"[REWRITE] {py_file}")
        if not dry_run:
            with open(py_file, "w", encoding="utf-8") as f:
                f.write(new_content)
```

# -----------------------------

# MAIN

# -----------------------------

def main():
parser = argparse.ArgumentParser()
parser.add_argument("--root", required=True, help="Path to picogl root")
parser.add_argument("--apply", action="store_true")
parser.add_argument("--dry-run", action="store_true")

```
args = parser.parse_args()
root = Path(args.root)

dry_run = not args.apply

print(f"Running in {'DRY RUN' if dry_run else 'APPLY'} mode")

# Step 1: Move files
for src, dst in MOVE_MAP.items():
    move_file(root, root, src, dst, dry_run=dry_run)

# Step 2: Rewrite imports
rewrite_imports(root, dry_run=dry_run)

print("Done.")
```

if **name** == "**main**":
main()
