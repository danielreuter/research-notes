#!/usr/bin/env python3
"""circuits-grid-models' labeller (adapted from vllm-epoch-run's). Stateless: every pass rebuilds its view from node 1's dispatcher
records and sweep dirs (gather.py) and from the store's labels, so any continuation can run it as is.

It labels the final run of every ended cov-gm* item (the 20 grid models' rows, questions.json) with ov.ws, ov.config, ov.gate and
ov.note. A failure's cause is CAUSES[key] when a reviewed cause is recorded there, else the stage line that failed.

    python3 label_loop.py once [--dry-run]     one pass
    python3 label_loop.py loop [EVERY_S]       a pass every EVERY_S (180) s, forever
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
BY = "circuits-grid-models"
RESEARCH = "/workspace/.venv/bin/research"
PREFIX = "cursor/grid-models-8c79 @ eda63fdd (cursor/coverage-v1-2622 @ 4764da87 + the 20 grid-model checkpoints and their workloads)"
QUESTIONS = json.loads((HERE / "questions.json").read_text())
#: one family id per publisher model series (circuits 07:19Z: base, instruct and coder together, R1 distills under their base)
FAMILY_OF = {"QWEN25_3B": "qwen25", "QWEN25_05B_INSTRUCT": "qwen25", "QWEN25_CODER_15B": "qwen25", "R1_DISTILL_QWEN_15B": "qwen25",
             "QWEN3_06B": "qwen3", "QWEN3_17B": "qwen3", "QWEN3_8B": "qwen3", "QWEN3_14B": "qwen3", "QWEN3_30B_A3B_2507": "qwen3",
             "LLAMA32_3B": "llama3", "LLAMA31_8B": "llama3", "R1_DISTILL_LLAMA_8B": "llama3", "SMOL17B": "smollm2",
             "MISTRAL7B_INSTRUCT": "mistral", "GEMMA2_9B": "gemma2", "OLMOE_0125_INSTRUCT": "olmoe", "PHI4": "phi", "YI15_6B": "yi",
             "FALCON3_1B": "falcon3", "FALCON3_7B": "falcon3"}
#: reviewed causes, by item key (cov-gmNNN): set when a stage line alone does not name the cause
CAUSES: dict[str, str] = json.loads((HERE / "causes.json").read_text()) if (HERE / "causes.json").exists() else {}
SSH = None


def research(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run([RESEARCH, *args], capture_output=True, text=True, timeout=300)


def ssh_cmd() -> list[str]:
    global SSH
    if SSH is None:
        SSH = research("pods", "ssh", "vy-nebius-1", "--print").stdout.split()
    return SSH


def gather() -> list[dict]:
    r = subprocess.run([*ssh_cmd(), "python3 -"], input=(HERE / "gather.py").read_text(), capture_output=True, text=True, timeout=300)
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


def desired(rec: dict) -> dict[str, str]:
    item = rec["key"].split("/", 1)[1]
    row = rec["row"] or QUESTIONS[item]["row"]
    passed = rec["state"] == "succeeded" and any(s.startswith("config PASS") and "460/460 equal" in s for s in rec["stages"])
    parts = [PREFIX]
    if "__stoch-" in row and rec["max_gates"] is not None:
        m = re.search(r"=(\d+)", rec["max_gates"] or "")
        parts.append(f"sampler Call one unit (MAX_GATES raised to {m.group(1)}); not provable in practice" if m
                     else "word check at the default MAX_GATES (no raise)")
    parts.append(f"question: {QUESTIONS[item]['q']}")
    if not passed:
        if item in CAUSES:
            parts.append(f"cause: {CAUSES[item]}")
        else:
            fail = next((s for s in reversed(rec["stages"]) if " FAIL " in s and "not run" not in s), None) or \
                   next((s for s in reversed(rec["stages"]) if " FAIL " in s), f"rc {rec['rc']} at task {rec['task']}")
            parts.append(f"failed: {fail[:300]}")
    return {"ov.ws": "coverage", "ov.config": row, "ov.gate": "pass" if passed else "fail", "ov.note": "; ".join(parts)}


def one_pass(dry: bool) -> None:
    recs = gather()
    Path("/tmp/gm-last-gather.jsonl").write_text("".join(json.dumps(r) + "\n" for r in recs))
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
