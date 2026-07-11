#!/usr/bin/env python3

import argparse
from pathlib import Path
import difflib

import libcst as cst
from libcst import matchers as m

# -----------------------------

# MODULE REWRITE RULES

# -----------------------------

MODULE_MAP = {
"picogl.backend.gl": "picogl.backend.gl",
"picogl.mode": "picogl.core.enums.mode",
"picogl.error": "picogl.core.error.gl_errors",
"picogl.state.draw_mode": "picogl.core.enums.draw_mode",
"picogl.wrappers": "picogl.backend.gl.wrappers",
"picogl.buffers": "picogl.gpu.buffers",
}

def rewrite_module_name(name: str) -> str:
for old, new in MODULE_MAP.items():
if name == old or name.startswith(old + "."):
return name.replace(old, new, 1)
return name

# -----------------------------

# TRANSFORMER

# -----------------------------

class ImportRewriteTransformer(cst.CSTTransformer):
    def leave_Import(self, original_node, updated_node):
        new_names = []
        for alias in updated_node.names:
            if isinstance(alias.name, cst.Attribute):
                full_name = self._get_full_name(alias.name)
            elif isinstance(alias.name, cst.Name):
                full_name = alias.name.value
            else:
                new_names.append(alias)
                continue

            new_name = rewrite_module_name(full_name)

            if new_name != full_name:
                new_node = self._build_name(new_name)
                new_names.append(alias.with_changes(name=new_node))
            else:
                new_names.append(alias)

        return updated_node.with_changes(names=new_names)

def leave_ImportFrom(self, original_node, updated_node):
    if updated_node.module is None:
        return updated_node

    module_name = self._get_full_name(updated_node.module)
    new_module_name = rewrite_module_name(module_name)

    if new_module_name != module_name:
        new_module = self._build_name(new_module_name)
        return updated_node.with_changes(module=new_module)

    return updated_node

# -----------------------------
# HELPERS
# -----------------------------

def _get_full_name(self, node):
    if isinstance(node, cst.Name):
        return node.value
    elif isinstance(node, cst.Attribute):
        return self._get_full_name(node.value) + "." + node.attr.value
    return ""

def _build_name(self, dotted_name: str):
    parts = dotted_name.split(".")
    node = cst.Name(parts[0])
    for part in parts[1:]:
        node = cst.Attribute(value=node, attr=cst.Name(part))
    return node
```

# -----------------------------

# FILE PROCESSING

# -----------------------------

def process_file(path: Path, apply: bool):
original_code = path.read_text()
module = cst.parse_module(original_code)

```
transformer = ImportRewriteTransformer()
modified = module.visit(transformer)

new_code = modified.code

if new_code != original_code:
    print(f"[MODIFIED] {path}")

    diff = difflib.unified_diff(
        original_code.splitlines(),
        new_code.splitlines(),
        fromfile="before",
        tofile="after",
        lineterm=""
    )

    print("\n".join(diff))

    if apply:
        path.write_text(new_code)
```

# -----------------------------

# RUNNER

# -----------------------------

def main():
parser = argparse.ArgumentParser()
parser.add_argument("--root", required=True)
parser.add_argument("--apply", action="store_true")
parser.add_argument("--dry-run", action="store_true")

```
args = parser.parse_args()
root = Path(args.root)

apply = args.apply and not args.dry_run

print(f"Running in {'APPLY' if apply else 'DRY RUN'} mode\n")

for py_file in root.rglob("*.py"):
    process_file(py_file, apply)

print("\nDone.")
```

if **name** == "**main**":
main()
