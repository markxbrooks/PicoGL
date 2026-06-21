#!/usr/bin/env python3

import argparse
from pathlib import Path
import difflib
import libcst as cst

STAGE_MAPS = {
    "backend": {
        "picogl.backend.gl": "picogl.backend.gl",
        "picogl.wrappers": "picogl.backend.gl.wrappers",
    },
    "enums": {
        "picogl.mode": "picogl.core.enums.mode",
        "picogl.state.draw_mode": "picogl.core.enums.draw_mode",
        "picogl.error": "picogl.core.errors.gl_errors",
    },
    "gpu": {
        "picogl.buffers": "picogl.gpu.buffers",
    },
}

EXACT_MAP = {
    "picogl.buffers.vertex.vbo.vbo_class":
        "picogl.gpu.buffers.vbo_types",
}

def module_exists(root: Path, module: str) -> bool:
    parts = module.split(".")[1:]
    path = root.joinpath(*parts)
    return (
        path.with_suffix(".py").exists()
        or path.joinpath("__init__.py").exists()
    )

def resolve_module(name: str, root: Path, active_maps):
    if name in EXACT_MAP:
        target = EXACT_MAP[name]
        if module_exists(root, target):
            return target, True
        return name, False

    for mapping in active_maps:
        for old, new in mapping.items():
            if name == old or name.startswith(old + "."):
                candidate = name.replace(old, new, 1)
                if module_exists(root, candidate):
                    return candidate, True
                return name, False

    return name, False

class ImportRewriteTransformer(cst.CSTTransformer):
    def __init__(self, root: Path, active_maps):
        self.root = root
        self.active_maps = active_maps

    def leave_Import(self, original_node, updated_node):
        new_names = []
        for alias in updated_node.names:
            full_name = self._get_full_name(alias.name)
            new_name, ok = resolve_module(full_name, self.root, self.active_maps)

            if ok and new_name != full_name:
                print(f"[REWRITE] {full_name} → {new_name}")
                new_node = self._build_name(new_name)
                new_names.append(alias.with_changes(name=new_node))
            else:
                if new_name != full_name:
                    print(f"[SKIPPED - TARGET MISSING] {full_name}")
                new_names.append(alias)

        return updated_node.with_changes(names=new_names)

    def leave_ImportFrom(self, original_node, updated_node):
        if updated_node.module is None:
            return updated_node

        module_name = self._get_full_name(updated_node.module)
        new_module, ok = resolve_module(module_name, self.root, self.active_maps)

        if ok and new_module != module_name:
            print(f"[REWRITE] {module_name} → {new_module}")
            new_node = self._build_name(new_module)
            return updated_node.with_changes(module=new_node)

        if new_module != module_name:
            print(f"[SKIPPED - TARGET MISSING] {module_name}")

        return updated_node

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

def process_file(path: Path, root: Path, active_maps, apply: bool):
    original_code = path.read_text()

    try:
        module = cst.parse_module(original_code)
    except Exception:
        print(f"[SKIP PARSE ERROR] {path}")
        return

    transformer = ImportRewriteTransformer(root, active_maps)
    modified = module.visit(transformer)

    new_code = modified.code

    if new_code != original_code:
        print(f"\n[MODIFIED] {path}")

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

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--stage", action="append", choices=["backend", "enums", "gpu"])

    args = parser.parse_args()
    root = Path(args.root)

    active_maps = []
    if args.stage:
        for stage in args.stage:
            active_maps.append(STAGE_MAPS[stage])

    print(f"Active stages: {args.stage or 'none'}")

    for py_file in root.rglob("*.py"):
        process_file(py_file, root, active_maps, args.apply)

    print("\nDone.")

if __name__ == "__main__":
    main()
