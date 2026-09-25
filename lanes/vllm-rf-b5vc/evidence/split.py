"""Split rules/vllm_bindings.py into the rules/vllm_bindings/ package by line ranges of the original (verbatim moves).

Run from integrations/vllm: python3 split.py <original.py> <out_dir>.  Imports are generated from the names each module uses.
"""
import ast
import os
import sys

ORIG, OUT = sys.argv[1], sys.argv[2]
PKG = "verity_vllm.program.frontend.rules.vllm_bindings"
lines = open(ORIG).read().splitlines()

# module -> (docstring, [inclusive 1-based line ranges of the original])
MODULES = {
    "pins": ("The kernel pins of the admitted profile (`verity_vllm/engine/profiles/vllm_d9105ea80_sm89_eager.py`) and the GEMM pins of the\nactive target.", [(42, 126), (321, 341)]),
    "observations": ("Fields observed on the construction host, and the one module state they live in (`_OBSERVED`).", [(129, 299)]),
    "operands": ("Operand helpers the binding rules share.", [(39, 40), (300, 320), (342, 353)]),
    "triton_launches": ("Direct Triton launches: the batch-invariant RMSNorm and GEMM.", [(354, 506)]),
    "attention": ("The KV cache write and the attention read (two ops).", [(507, 728)]),
    "elementwise": ("Generic elementwise / activation bindings.", [(729, 870)]),
    "norm_chain": ("The unfused norm chain: `forward_native` norms as ATen on an f32 copy.", [(871, 1274)]),
    "fp8": ("The block-scaled FP8 linear and the same-dtype cast it ends with.", [(1275, 1454)]),
    "fused_norm": ("Fused add + RMSNorm under the batch-invariant dispatch, derived.", [(1455, 1484)]),
    "views": ("Views of allocations and the token-id widening.", [(1485, 1545)]),
    "cache_pad": ("The padded engine's step-boundary cache clear over implicit KV state.", [(1546, 1625)]),
    "collectives": ("Tensor-parallel collectives: the `verity_tp::*` ops the construction's CollectiveBus emits.", [(1626, 1873)]),
    "__init__": (None, [(1, 23), (1874, 1895)]),
}
DROPPED = [(24, 38), (1896, 1905)]  # the original's imports and `__all__`
INIT_REEXPORTS = {  # names importers use (library + tests), beyond what __init__'s own code needs
    "GEMM_PINS", "RMS_PINS", "MEAN_PINS", "tuned_gemm_table_sha256", "gemm_pins_for", "lookup_key", "_pins_ok",
    "observe_attention_impls", "observe_export_facts", "observe_target_profile", "declared_derived_accounting",
    "clear_observations", "observe_launch_context", "active_target_profile", "_OBSERVED",
    "AllocViewRule", "TritonGemmRule", "triton_launch"}

covered = sorted([r for _, rs in MODULES.values() for r in rs] + DROPPED)
n = 1
for a, b in covered:
    assert a >= n and not any(x.strip() for x in lines[n - 1:a - 1]), (a, n)
    n = b + 1
assert n == len(lines) + 1, (n, len(lines))

# the original's imports: name -> (module, original name)
tree = ast.parse("\n".join(lines))
EXTERNAL = {}
EXTERNAL_ORDER = []
for s in tree.body:
    if isinstance(s, ast.ImportFrom) and s.module != "__future__":
        EXTERNAL_ORDER.append(s.module)
        for a in s.names:
            EXTERNAL[a.asname or a.name] = (s.module, a.name)
    elif isinstance(s, ast.Import):
        for a in s.names:
            EXTERNAL[a.asname or a.name] = (None, a.name)


def chunk_text(ranges):
    parts = []
    for a, b in ranges:
        seg = lines[a - 1:b]
        while seg and not seg[0].strip():
            seg = seg[1:]
        while seg and not seg[-1].strip():
            seg = seg[:-1]
        parts.append("\n".join(seg))
    return parts


def defined(text):
    out = set()
    for s in ast.parse(text).body:
        if isinstance(s, (ast.FunctionDef, ast.ClassDef)):
            out.add(s.name)
        elif isinstance(s, ast.Assign):
            out |= {n.id for t in s.targets for n in ast.walk(t) if isinstance(n, ast.Name)}
        elif isinstance(s, ast.AnnAssign):
            out.add(s.target.id)
    return out


def used(text):
    t = ast.parse(text)
    return {n.id for n in ast.walk(t) if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load)}


bodies = {m: chunk_text(rs) for m, (_, rs) in MODULES.items()}
OWNER = {}
for m, parts in bodies.items():
    for name in defined("\n\n".join(parts)):
        assert name not in OWNER, name
        OWNER[name] = m


def import_line(mod, names):
    names = sorted(names)
    line = f"from {mod} import {', '.join(names)}"
    if len(line) <= 150:
        return line
    head = f"from {mod} import ("
    out, cur = [], head
    for i, nm in enumerate(names):
        piece = nm + (", " if i < len(names) - 1 else ")")
        if len(cur) + len(piece.rstrip()) > 150:
            out.append(cur.rstrip())
            cur = " " * len(head) + piece
        else:
            cur += piece
    out.append(cur)
    return "\n".join(out)


def imports_for(m, need):
    ext = {}
    plain = []
    sib = {}
    for name in sorted(need):
        if OWNER.get(name) == m:
            continue
        if name in OWNER:
            sib.setdefault(OWNER[name], []).append(name)
        elif name in EXTERNAL:
            mod, orig = EXTERNAL[name]
            if mod is None:
                plain.append(orig)
            else:
                ext.setdefault(mod, []).append(orig if orig == name else f"{orig} as {name}")
    out = ["from __future__ import annotations", ""]
    if plain:
        out += [f"import {p}" for p in sorted(set(plain))] + [""]
    for mod in EXTERNAL_ORDER:
        if mod in ext:
            out.append(import_line(mod, ext[mod]))
    for sm in sorted(sib):
        out.append(import_line(f"{PKG}.{sm}", sib[sm]))
    return "\n".join(out)


def wrap_all(names):
    out, cur = [], "__all__ = ["
    for i, nm in enumerate(names):
        piece = f'"{nm}"' + (", " if i < len(names) - 1 else "]")
        if len(cur) + len(piece.rstrip()) > 150:
            out.append(cur.rstrip())
            cur = "           " + piece
        else:
            cur += piece
    out.append(cur)
    return "\n".join(out)


os.makedirs(OUT, exist_ok=True)
for m, (doc, _) in MODULES.items():
    parts = bodies[m]
    if m == "__init__":
        docstring, code = parts[0], parts[1:]
        need = used("\n\n".join(code)) | INIT_REEXPORTS
    else:
        docstring, code = f'"""{doc}"""', parts
        need = used("\n\n".join(code))
    text = docstring + "\n\n" + imports_for(m, need) + "\n"
    if code:
        text += "\n\n" + "\n\n\n".join(code) + "\n"
    if m == "__init__":
        exported = sorted(INIT_REEXPORTS - {"AllocViewRule", "TritonGemmRule"} | {"VLLM_BINDING_RULES", "vllm_ruleset", "AllocViewRule", "TritonGemmRule"})
        text += "\n\n" + wrap_all(exported) + "\n"
    with open(os.path.join(OUT, f"{m}.py"), "w") as f:
        f.write(text)
    print(f"{m}.py {len(text.splitlines())} lines")
