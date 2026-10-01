#!/usr/bin/env python3
"""circuits-grid-models' labeller (adapted from vllm-epoch-run's). Stateless: every pass rebuilds its view from node 1's dispatcher
records and sweep dirs (gather.py) and from the store's labels, so any continuation can run it as is.

It labels the final run of every ended cov-gm* item (the 20 grid models' rows, questions.json) with ov.ws, ov.config, ov.gate and
ov.note. A failure's cause is CAUSES[key] when a reviewed cause is recorded there, else the stage line that failed.

    python3 label_loop.py once [--dry-run]     one pass
    python3 label_loop.py loop [EVERY_S]       a pass every EVERY_S (180) s, forever

On vy-nebius-1 (as research, from /workspace/jobs/gm-label) it reads the dispatcher's records and sweep dirs in place, runs the
research CLI of NODE_TREE with the store credentials of the `research-r2` Secret the Jobs use (read each pass, never printed), and
keeps its local store and silu_check's venv beside it; anywhere else it reaches node 1 over `research pods ssh`.
"""
from __future__ import annotations

import base64
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
BY = "circuits-grid-models"
RESEARCH = "/workspace/.venv/bin/research"
ON_NODE = Path("/workspace/jobs/dispatch/log.jsonl").exists()
NODE_TREE = "/workspace/research/trees/cursor-grid-boundary-gm-827a"
NODE_ENV: dict[str, str] | None = None
PREFIX = "cursor/grid-models-8c79 @ b9880ac1 (cursor/coverage-v1-2622 @ 90ebe43d + the 20 grid-model checkpoints and their workloads)"
#: each job tree an item's Build was submitted from (gather's `tree`), as its note names it
TREES = {"/workspace/research/trees/cursor-grid-models-8c79": PREFIX,
         "/workspace/research/trees/cursor-grid-plan-gm-827a": (
             "cursor/grid-plan-gm-827a @ 05fa9d3e (cursor/grid-models-8c79 @ b9880ac1 + cursor/grid-plan-cov-827a @ 04908a9a: "
             "coverage-v1 @ 90c6d897 with the Commit's plan derived in the Build, the replay store written in a thread, "
             "VERITY_DENSE_THREADS; note:20261001T1038Z-handoff-from-circuits-commit-phases-plan-tree)"),
         "/workspace/research/trees/cursor-grid-boundary-gm-827a": (
             "cursor/grid-boundary-gm-827a @ 1fff7995 (the plan tree cursor/grid-plan-gm-827a @ 05fa9d3e + the Build's call-boundary "
             "plan read by the Commit; note:20261001T1417Z-handoff-from-circuits-commit-phases-boundary-gm-tree)"),
         "/workspace/research/trees/cursor-grid-models-more-be5a": (
             "cursor/grid-models-more-be5a @ 70471454 (the boundary tree cursor/grid-boundary-gm-827a @ 1fff7995 + 3 more checkpoints "
             "and their workloads; note:20261001T1636Z-handoff-from-circuits-grid-models-pk3-three-models-reorder)")}
QUESTIONS = json.loads((HERE / "questions.json").read_text())
#: one family id per publisher model series (circuits 07:19Z: base, instruct and coder together, R1 distills under their base)
FAMILY_OF = {"QWEN25_3B": "qwen25", "QWEN25_05B_INSTRUCT": "qwen25", "QWEN25_CODER_15B": "qwen25", "R1_DISTILL_QWEN_15B": "qwen25",
             "QWEN3_06B": "qwen3", "QWEN3_17B": "qwen3", "QWEN3_8B": "qwen3", "QWEN3_14B": "qwen3", "QWEN3_30B_A3B_2507": "qwen3",
             "LLAMA32_3B": "llama3", "LLAMA31_8B": "llama3", "R1_DISTILL_LLAMA_8B": "llama3", "SMOL17B": "smollm2",
             "MISTRAL7B_INSTRUCT": "mistral", "GEMMA2_9B": "gemma2", "OLMOE_0125_INSTRUCT": "olmoe", "PHI4": "phi", "YI15_6B": "yi",
             "FALCON3_1B": "falcon3", "FALCON3_7B": "falcon3", "PLEIAS_350M": "pleias", "DANUBE3_500M": "danube",
             "SALAMANDRA_2B": "salamandra"}
#: reviewed causes, by item key (cov-gmNNN): set when a stage line alone does not name the cause
CAUSES: dict[str, str] = json.loads((HERE / "causes.json").read_text()) if (HERE / "causes.json").exists() else {}
#: silu_check.py's verdict on a SiluMul_v1 replay mismatch, by item key ("" = checked, not that edge); filled by one_pass
AUTO = HERE / "causes_auto.json"
SILU_EDGE = ("Definition gap, not a Commit fault: SiluMul_v1's expf-overflow edge (a gate <= -89, where the GPU's silu is g/inf = -0 "
             "and SiluMulBf16_v1 a tiny g*e^g); the quarantined SiluMul_v2 (lane vllm-coverage-defs, the red-team's sm_120 edge words) "
             "equals the committed words of every mismatched row (labeller/silu_check.py): ")
SSH = None


def node_env() -> dict[str, str]:
    """The research CLI's environment on node 1: NODE_TREE's package, a store beside this script, the Secret's R2 settings."""
    r = subprocess.run(["kubectl", "get", "secret", "research-r2", "-o", "json"], capture_output=True, text=True, timeout=120,
                       env={**os.environ, "KUBECONFIG": os.path.expanduser("~/.kube/config")})
    if r.returncode:
        raise RuntimeError(f"secret research-r2: kubectl rc {r.returncode}")
    sec = {k: base64.b64decode(v).decode() for k, v in json.loads(r.stdout)["data"].items()}
    return {**os.environ, **sec, "PYTHONPATH": f"{NODE_TREE}/tools/research/src", "RESEARCH_STORE": str(HERE / "store")}


def research(*args: str) -> subprocess.CompletedProcess:
    if ON_NODE:
        return subprocess.run([sys.executable, "-m", "research", *args], capture_output=True, text=True, timeout=300, env=NODE_ENV)
    return subprocess.run([RESEARCH, *args], capture_output=True, text=True, timeout=300)


def ssh_cmd() -> list[str]:
    global SSH
    if SSH is None:
        SSH = research("pods", "ssh", "vy-nebius-1", "--print").stdout.split()
    return SSH


def gather() -> list[dict]:
    cmd = [sys.executable, str(HERE / "gather.py")] if ON_NODE else [*ssh_cmd(), "python3 -"]
    r = subprocess.run(cmd, input=None if ON_NODE else (HERE / "gather.py").read_text(), capture_output=True, text=True, timeout=300)
    if r.returncode:
        raise RuntimeError(f"gather: {r.stderr.strip()[-300:]}")
    return [json.loads(ln) for ln in r.stdout.splitlines() if ln.strip()]


def current(run: str) -> dict[str, tuple[str, str]]:
    r = research("data", "labels", run, "--remote", "--json")
    out: dict[str, tuple[str, str]] = {}
    try:
        labels = json.loads(r.stdout)["labels"]
    except (json.JSONDecodeError, KeyError):
        raise RuntimeError(f"labels {run}: {(r.stderr or r.stdout).strip()[-300:]}")
    for x in sorted((x["label"] for x in labels), key=lambda lab: lab["ts"]):
        if x["by"] == BY:
            out[x["key"]] = (x["value"], x["ts"])
    return out


def base_of(item: str) -> str:
    """cov-gmNNN for an item or any of its packed golden twins (-pk, -pk2, -pk3)."""
    return re.sub(r"-pk\d*$", "", item)


def desired(rec: dict) -> dict[str, str]:
    item = rec["key"].split("/", 1)[1]
    base = base_of(item)
    row = rec["row"] or QUESTIONS[base]["row"]
    passed = rec["state"] == "succeeded" and any(s.startswith("config PASS") and "460/460 equal" in s for s in rec["stages"])
    parts = [TREES.get(rec.get("tree") or "", f"tree {rec.get('tree')}" if rec.get("tree") else PREFIX)]
    if base != item:
        second = (" (the second, submitted once PACK_MODELS listed the model; "
                  "note:20261001T1412Z-handoff-from-circuits-drop-deadline-gate)") if item.endswith("-pk2") else (
            " (the third, with its Build kept on vy-nebius-1 so its Commit routes and packs; "
            "note:20261001T1555Z-handoff-from-circuits-1130-set)") if item.endswith("-pk3") else ""
        parts.append(f"packed golden twin of {base}{second} (note:20261001T1158Z-handoff-from-circuits-refill-node2-pack-goldens), "
                     + (f"its Commit packed in {rec['packed']}" if rec.get("packed") else "its Commit not packed"))
    if rec.get("on") == "vy-nebius-2":
        parts.append("Commit and replay on vy-nebius-2 (n2_commit.sh offload; the Build on vy-nebius-1)")
    if "__stoch-" in row and rec["max_gates"] is not None:
        m = re.search(r"=(\d+)", rec["max_gates"] or "")
        parts.append(f"sampler Call one unit (MAX_GATES raised to {m.group(1)}); not provable in practice" if m
                     else "word check at the default MAX_GATES (no raise)")
    parts.append(f"question: {QUESTIONS[base]['q']}")
    auto = json.loads(AUTO.read_text()) if AUTO.exists() else {}
    if not passed:
        if item in CAUSES:
            parts.append(f"cause: {CAUSES[item]}")
        elif auto.get(item):
            parts.append(f"cause: {auto[item]}")
        else:
            fail = next((s for s in reversed(rec["stages"]) if " FAIL " in s and "not run" not in s), None) or \
                   next((s for s in reversed(rec["stages"]) if " FAIL " in s), f"rc {rec['rc']} at task {rec['task']}")
            parts.append(f"failed: {fail[:300]}")
    return {"ov.ws": "coverage", "ov.config": row, "ov.gate": "pass" if passed else "fail", "ov.note": "; ".join(parts)}


def silu_cause(item: str) -> str:
    """SILU_EDGE plus each mismatched row's elements when silu_check.py finds v2 equal on every SiluMul_v1 mismatch, else ""."""
    if ON_NODE:
        cmd, cwd = [str(HERE / ".venv/bin/python"), str(HERE / "silu_check.py"), item], str(HERE)
        env = {**os.environ, "PYTHONPATH": f"{NODE_TREE}/packages/verity/src:{NODE_TREE}/integrations/vllm"}
    else:
        cmd, cwd, env = ["/workspace/.venv/bin/python", str(HERE / "silu_check.py"), item], "/workspace/integrations/vllm", None
    r = subprocess.run(cmd, cwd=cwd, env=env, capture_output=True, text=True, timeout=900)
    rows = re.findall(r": (\S+) (r\d+) step (\d+) row (\d+): v1 differs at (\d+) of \d+ elements, v2 at (\d+)", r.stdout)
    if r.returncode or not rows or any(v2 != "0" or n == "0" for *_, n, v2 in rows):
        return ""
    gates = re.findall(r"gate 0x[0-9a-f]{4} \((-?[\d.]+)\)", r.stdout)
    return SILU_EDGE + "; ".join(f"{op} {rid} step {st} row {row}: {n} element(s)" for op, rid, st, row, n, _ in rows) + \
        f" (gates {', '.join(sorted(set(gates)))})"


def fill_auto(recs: list[dict]) -> None:
    auto = json.loads(AUTO.read_text()) if AUTO.exists() else {}
    for rec in recs:
        item = rec["key"].split("/", 1)[1]
        if item in CAUSES or item in auto or rec["state"] == "succeeded" or not any("SiluMul_v1" in s for s in rec["stages"]):
            continue
        try:
            auto[item] = silu_cause(item)
        except (subprocess.SubprocessError, OSError) as e:
            print(f"{item}: silu_check failed: {e}", flush=True)
            continue
        print(f"{item}: silu_check -> {auto[item][-160:] or 'not the expf-overflow edge'}", flush=True)
        AUTO.write_text(json.dumps(auto, indent=1, sort_keys=True) + "\n")


def one_pass(dry: bool) -> None:
    global NODE_ENV
    if ON_NODE:
        NODE_ENV = node_env()
    recs = gather()
    Path("/tmp/gm-last-gather.jsonl").write_text("".join(json.dumps(r) + "\n" for r in recs))
    fill_auto(recs)
    for rec in recs:
        key = rec["key"]
        if not rec["runs"] or not rec["row"]:
            print(f"{key}: ended {rec['state']} but no run or row found yet", flush=True)
            continue
        run = rec["runs"][-1]
        have = current(run)
        want = desired(rec)
        todo = {k: v for k, v in want.items() if have.get(k, (None,))[0] != v}
        for k, v in todo.items():
            if dry:
                print(f"DRY {key} {run} {k}={v[:160]}", flush=True)
                continue
            r = research("data", "label", run, k, v, "--by", BY, "--off-vocab")
            print(f"{time.strftime('%H:%M:%SZ', time.gmtime())} {key} {run} {k}={v[:100]} rc={r.returncode} "
                  f"{(r.stdout.strip().splitlines() or [''])[-1][:120]}{' ' + r.stderr.strip()[-200:] if r.returncode else ''}", flush=True)


def main(argv: list[str]) -> int:
    if argv[:1] == ["once"]:
        one_pass("--dry-run" in argv)
    elif argv[:1] == ["loop"]:
        every = int(argv[1]) if len(argv) > 1 else 180
        while True:
            try:
                one_pass(False)
                print(f"{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())} pass ok", flush=True)
            except Exception as e:  # noqa: BLE001  (a failed pass is retried next time)
                print(f"{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())} pass failed: {e}", flush=True)
            time.sleep(every)
    else:
        print(__doc__)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
