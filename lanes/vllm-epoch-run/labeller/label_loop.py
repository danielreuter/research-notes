#!/usr/bin/env python3
"""vllm-epoch-run's labeller since 1 Oct 05:55Z (bc-21460bd7, continuing bc-75fd4007). Stateless: every pass rebuilds its view from node 1's
dispatcher records and sweep dirs (gather.py) and from the store's labels, so any continuation can run it as is.

It labels the final run of
  - circuits' Gemma-2 items cov-cg01..cg18 (adopted; circuits 04:36Z): after the old feeder has labelled one (or ADOPT_WAIT_S after it
    ended), it writes the labels this script computes wherever they differ, which corrects the old feeder's note on the stochastic rows
    (it claimed the MAX_GATES raise, which circuits' submits never set);
  - this lane's own submits (MINE);
  - the two node-2 duplicates that ran anyway (DUPS), with a note naming the item they duplicate.

    python3 label_loop.py once [--dry-run]     one pass
    python3 label_loop.py loop [EVERY_S]       a pass every EVERY_S (180) s, forever (tmux `epoch-label`)
"""
from __future__ import annotations

import calendar
import json
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
BY = "vllm-epoch-run"
ADOPT_WAIT_S = 900
PREFIX = ("pre-merge #503 #557 #598 #599 #611 #619 #620 #621 #622 #623 #624 tp2-gpuless-build@4009ec30 "
          "tp2-commit-token-budget@b642a4a4 @ 5bab849b on main 73eee493")
Q = ("Do Gemma-2-2B's softcap, normalizer and tied-embedding Programs hold across the grid's batch sizes, sampling modes and lengths "
     "on sm_120?")
ADOPT = {f"vllm-epoch-run/cov-cg{i:02d}" for i in range(1, 19)}
MINE = {f"vllm-epoch-run/cov-{c}-2": "circuits 05:55Z: B64 go while disk stays under the steward's latches"
        for c in ("m001", "n048", "n049", "n050", "n051", "n052")}
DUPS = {"vllm-epoch-run/cov-m005-2": "cov-cg12", "vllm-epoch-run/cov-m007-2": "cov-cg01"}
WORD_CAUSE = ("word check: GumbelTopPTokenSelect_v2 V=256000 too large for Q_word W=32 (the B1 sampler of top-p and Gumbel alike; a "
              "served-sampler Definition fix is on circuits' backlog, no rerun until it lands). Submitted without the grid cell's "
              "VERITY_QWORD_MAX_GATES raise; n031 (B1 256/32 top-p) with that raise passes 460/460 but is one unprovable unit")
SSH = None


def research(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["research", *args], capture_output=True, text=True, timeout=300)


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


def epoch(t: str) -> float:
    return calendar.timegm(time.strptime(t, "%Y-%m-%dT%H:%M:%SZ"))


def desired(rec: dict) -> dict[str, str]:
    key, row, item = rec["key"], rec["row"] or "", rec["key"].split("/", 1)[1]
    passed = rec["state"] == "succeeded" and any(s.startswith("config PASS") and "460/460 equal" in s for s in rec["stages"])
    stoch = "__stoch-" in row
    parts = [PREFIX]
    if key in ADOPT:
        parts.append(f"submitted by circuits as {item} (9:38 PM PDT), adopted by vllm-epoch-run")
    elif key in MINE:
        parts.append(MINE[key])
    if stoch and rec["max_gates"] is not None:
        parts.append("sampler Call one unit (MAX_GATES raised to 225000000); not provable in practice" if rec["max_gates"]
                     else "word check at the default MAX_GATES (no raise)")
    parts.append(f"question: {Q}")
    if key in DUPS:
        parts = [PREFIX, f"duplicate of {DUPS[key]} (same row; released twice at 04:44Z, ran on node 2's Build and node 1's Commit before "
                         f"it could be dropped); its run root matches {DUPS[key]}'s", f"question: {Q}"]
        return {"ov.config": row, "ov.note": "; ".join(parts)}
    if not passed:
        if rec["rc"] == 13 and "__b1__" in row and stoch:
            parts.append(WORD_CAUSE)
        else:
            fail = next((s for s in reversed(rec["stages"]) if " FAIL " in s and "not run" not in s), None) or \
                   next((s for s in reversed(rec["stages"]) if " FAIL " in s), f"rc {rec['rc']}")
            parts.append(f"failed: {fail[:300]}")
    return {"ov.ws": "coverage", "ov.config": row, "ov.gate": "pass" if passed else "fail", "ov.note": "; ".join(parts)}


def one_pass(dry: bool) -> None:
    now = time.time()
    for rec in gather():
        key = rec["key"]
        if key not in ADOPT and key not in MINE and key not in DUPS:
            continue
        if not rec["runs"] or not rec["row"]:
            print(f"{key}: ended {rec['state']} but no run or row found yet", flush=True)
            continue
        run = rec["runs"][-1]
        have = current(run)
        if key in ADOPT and "ov.gate" not in have and now - epoch(rec["t"]) < ADOPT_WAIT_S:
            continue
        want = desired(rec)
        todo = {k: v for k, v in want.items() if have.get(k, (None,))[0] != v}
        for k, v in todo.items():
            if dry:
                print(f"DRY {key} {run} {k}={v[:120]}", flush=True)
                continue
            r = research("data", "label", run, k, v, "--by", BY, "--off-vocab")
            print(f"{time.strftime('%H:%M:%SZ', time.gmtime())} {key} {run} {k}={v[:100]} rc={r.returncode}"
                  f"{' ' + r.stderr.strip()[-200:] if r.returncode else ''}", flush=True)


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
