#!/usr/bin/env python3
"""The 11:30 counts (note:20261001T1555Z-handoff-from-circuits-1130-set), on vy-nebius-1: ended deployments of the grid (the labeller's
last gather, cov-gm* and their twins) and of the rest of the epoch run (every other `vllm-epoch-run/*` item's final record in
done.jsonl, or its row's .n2-replay marker when its Commit replayed on node 2), each split by node, then models and families with an
ended deployment and with a pass, across both. An epoch-run item's model is its row's first field; its stage is the last line of
its row's stages.txt (the epoch run's failures are audited by another worker). `python3 counts_all.py [GATHER.jsonl]`"""
import collections
import json
import re
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from label_loop import FAMILY_OF, base_of, desired  # noqa: E402

ROOT = Path("/workspace/jobs/dispatch")
COV = Path("/workspace/jobs/cov")
GRID = re.compile(r"vllm-epoch-run/cov-gm\d{3}")
#: model id prefix -> family, for rows outside the grid (the grid's come from FAMILY_OF by role); the longest prefix wins
PREFIX_FAMILY = {"gemma2": "gemma2", "llama3": "llama3", "mistral": "mistral", "olmoe": "olmoe", "phi3": "phi", "phi4": "phi",
                 "pythia": "pythia", "qwen25": "qwen25", "qwen3": "qwen3", "smollm2": "smollm2", "tinyllama": "tinyllama",
                 "falcon3": "falcon3", "yi15": "yi", "r1-distill-qwen": "qwen25", "r1-distill-llama": "llama3", "pleias": "pleias",
                 "danube3": "danube", "salamandra": "salamandra"}


def family(model: str) -> str:
    hits = [p for p in PREFIX_FAMILY if model.startswith(p)]
    return PREFIX_FAMILY[max(hits, key=len)] if hits else f"? ({model})"


Q = json.loads((HERE / "questions.json").read_text())
grid = [json.loads(ln) for ln in Path(sys.argv[1] if len(sys.argv) > 1 else "/tmp/gm-last-gather.jsonl").read_text().splitlines()
        if ln.strip()]
log = [json.loads(ln) for ln in (ROOT / "log.jsonl").read_text().splitlines() if '"ev": "moved"' in ln]
built_n2 = {e["key"] for e in log if "-build-" in e.get("job", "")}
moved = {e["key"] for e in log}

per_model = collections.defaultdict(lambda: [0, 0, ""])
g_node, g_causes, g_pass = collections.Counter(), collections.Counter(), 0
for r in grid:
    item = r["key"].split("/", 1)[1]
    role = Q[base_of(item)]["role"]
    model = (r["row"] or Q[base_of(item)]["row"]).split("__")[0]
    want = desired(r)
    ok = want["ov.gate"] == "pass"
    g_pass += ok
    per_model[model][0 if ok else 1] += 1
    per_model[model][2] = FAMILY_OF[role]
    g_node[("Build n2" if r["key"] in built_n2 else "Build n1", "Commit n2" if r.get("on") == "vy-nebius-2" else "Commit n1")] += 1
    if not ok:
        m = re.search(r"cause: (.{0,90})", want["ov.note"])
        g_causes[(m.group(1) if m else want["ov.note"][-90:]).split(":")[0]] += 1

ep = {}
for ln in (ROOT / "done.jsonl").read_text().splitlines():
    if '"vllm-epoch-run/' in ln and not GRID.search(ln):
        e = json.loads(ln)
        ep[e["key"]] = e
for key in moved - ep.keys():
    if key.startswith("vllm-epoch-run/") and not GRID.match(key):
        for mk in (COV / key.split("/", 1)[1]).glob("*/.n2-replay"):
            parts = mk.read_text().split()
            if len(parts) == 2 and parts[1] == "0":
                ep[key] = {"key": key, "state": "succeeded", "rc": 0, "on": "vy-nebius-2",
                           "t": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(mk.stat().st_mtime))}
e_node, e_stages, e_pass = collections.Counter(), collections.Counter(), 0
for key, e in ep.items():
    item = key.split("/", 1)[1]
    rows = sorted(p for p in (COV / item).glob("*__tp*") if p.is_dir()) if (COV / item).is_dir() else []
    model = rows[0].name.split("__")[0] if rows else "(no row dir)"
    ok = e.get("state") == "succeeded"
    e_pass += ok
    per_model[model][0 if ok else 1] += 1
    per_model[model][2] = per_model[model][2] or family(model)
    e_node[("Build n2" if key in built_n2 else "Build n1", "Commit n2" if e.get("on") == "vy-nebius-2" else "Commit n1")] += 1
    if not ok:
        last = ""
        if rows and (rows[0] / "stages.txt").exists():
            lines = [x for x in (rows[0] / "stages.txt").read_text(errors="replace").splitlines()
                     if x.strip() and not x.startswith(("release ", "precheck"))]
            last = lines[-1] if lines else ""
        m = re.search(r"config FAIL \S+ (.*)$", last)
        e_stages[(m.group(1) if m else last or "no stages.txt").split(":")[0][:60]] += 1

print(f"grid: ended {len(grid)}, pass {g_pass}, fail {len(grid) - g_pass}; by node (Build, Commit): "
      + ", ".join(f"{b}/{c} {n}" for (b, c), n in sorted(g_node.items())))
for c, n in g_causes.most_common():
    print(f"  grid fail {n}: {c}")
print(f"epoch run (the rest of vllm-epoch-run): ended {len(ep)}, succeeded {e_pass}, failed {len(ep) - e_pass}; by node (Build, Commit): "
      + ", ".join(f"{b}/{c} {n}" for (b, c), n in sorted(e_node.items())))
for c, n in e_stages.most_common():
    print(f"  epoch fail {n}: {c}")
real = {m: v for m, v in per_model.items() if m != "(no row dir)"}
fams = {v[2] for v in real.values()}
print(f"both: ended {len(grid) + len(ep)}; models {len(real)} (with a pass {sum(1 for v in real.values() if v[0])}); "
      f"families {len(fams)} (with a pass {len({v[2] for v in real.values() if v[0]})}): {', '.join(sorted(fams))}")
for m, (p, f, fam) in sorted(per_model.items(), key=lambda kv: (kv[1][2], kv[0])):
    print(f"  {m:22s} {fam:10s} pass {p:3d} fail {f}")
