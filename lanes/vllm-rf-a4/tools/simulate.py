"""Simulate the move map on the import graph: package cycles, module cycles and layers before/after.

usage: python simulate.py REPO
"""
from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import graph as G  # noqa: E402
import movemap as M  # noqa: E402

NEW_LAYER = {
    "verity_vllm": "pipeline",
    "verity_vllm.config": "config",
    "verity_vllm.target_family": "config",
    "verity_vllm.pipeline": "pipeline",
    "verity_vllm.check": "check|properties",
    "verity_vllm.properties": "check|properties",
    "verity_vllm.acquire": "acquire",
    "verity_vllm.observe": "observe|commit",
    "verity_vllm.commit": "observe|commit",
    "verity_vllm.engine": "engine",
    "verity_vllm.query": "query|correspondence",
    "verity_vllm.correspondence": "query|correspondence",
    "verity_vllm.program": "program",
    "verity_vllm.collectives": "collectives",
    "verity_vllm.query.boundary": "core",
    "verity_vllm.query.partition": "core",
    "verity_vllm.program.frontend.liveness": "core",
}
LAYERS = ("tests", "pipeline", "check|properties", "acquire", "observe|commit", "engine", "query|correspondence",
          "program", "collectives", "config", "core")
RANK = {n: len(LAYERS) - i for i, n in enumerate(LAYERS)}


def interim(repo: Path) -> dict:
    src = (repo / "integrations/vllm/tests/lint/_imports.py").read_text()
    tree = ast.parse(src)
    for node in tree.body:
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "INTERIM_LAYER":
            return ast.literal_eval(node.value)
    raise SystemExit("no INTERIM_LAYER")


def layer_of(m: str, table: dict) -> str:
    parts = m.split(".")
    for i in range(len(parts), 0, -1):
        hit = table.get(".".join(parts[:i]))
        if hit:
            return hit
    raise KeyError(m)


def moves():
    out = []
    for _, g in M.GROUPS:
        out += g
    return out


def map_path(rel: str) -> str:
    """verity_vllm-relative path -> new path after every move (in order)."""
    for old, new in moves():
        if rel == old:
            rel = new
        elif rel.startswith(old.rstrip("/") + "/"):
            rel = new + rel[len(old):]
    return rel


def mod_of(rel: str) -> str:
    parts = ["verity_vllm", *Path(rel).with_suffix("").parts]
    if parts[-1] == "__init__":
        parts.pop()
    return ".".join(parts)


def main():
    repo = Path(sys.argv[1])
    pkg = repo / "integrations/vllm/verity_vllm"
    known, es = G.edges(pkg)
    to_tests = {mod_of(o.removeprefix("verity_vllm/")) for o, _ in M.TO_TESTS}
    ren = {}
    for m, p in known.items():
        rel = str(p.relative_to(pkg))
        ren[m] = mod_of(map_path(rel))
    # collisions
    inv = {}
    for a, b in ren.items():
        inv.setdefault(b, []).append(a)
    for b, a in inv.items():
        if len(a) > 1:
            print("COLLISION", b, a)
    old_layer = interim(repo)
    bad = 0
    for m in sorted(known):
        if m in to_tests:
            continue
        lo, ln = layer_of(m, old_layer), layer_of(ren[m], NEW_LAYER)
        if lo != ln:
            bad += 1
            print(f"LAYER CHANGE {m} ({lo}) -> {ren[m]} ({ln})")
    print("layer changes:", bad)
    es2 = [(ren[a], ren[b], f, ln) for a, b, f, ln in es if a not in to_tests and b not in to_tests]
    old_pc = G.package_cycles(es)
    new_pc = G.package_cycles(es2)
    print(f"package cycles: {len(old_pc)} -> {len(new_pc)}")
    for c in new_pc:
        print("  new pkg-cycle", c)
    # module sccs
    adj = {}
    for a, b, *_ in es2:
        adj.setdefault(a, set()).add(b)
    new_known = {ren[m] for m in known if m not in to_tests}
    for c in G.sccs(new_known, adj):
        print("  scc", " <-> ".join(x.removeprefix("verity_vllm.") for x in c))
    # layer violations old vs new
    def viol(edges, table):
        out = set()
        for a, b, *_ in edges:
            if RANK[layer_of(a, table)] < RANK[layer_of(b, table)]:
                out.add((a, b))
        return out
    vo = viol([e for e in es if e[0] not in to_tests and e[1] not in to_tests], old_layer)
    vn = viol(es2, NEW_LAYER)
    vo_mapped = {(ren[a], ren[b]) for a, b in vo}
    print(f"layer violations (unique pairs): {len(vo)} -> {len(vn)}; new-not-old {len(vn - vo_mapped)}; gone {len(vo_mapped - vn)}")
    for a, b in sorted(vn - vo_mapped):
        print("  NEW", a, "->", b)
    if len(sys.argv) > 2 and sys.argv[2] == "map":
        for m in sorted(known):
            if ren[m] != m:
                print("MAP", m, ren[m])


if __name__ == "__main__":
    main()
