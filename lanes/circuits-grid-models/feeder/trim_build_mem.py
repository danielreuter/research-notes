#!/usr/bin/env python3
"""Trim the Build memory requests (resources.build.memory, GB) of gm-feed's unsubmitted items to measured peaks with headroom, so more
Builds admit under deployments-cpu's memory quota (circuits, 7:55 AM PDT). On vy-nebius-1, as research:

    python3 trim_build_mem.py              the mapping, one line per class, and what would change
    python3 trim_build_mem.py --validate   leave one out: how often the rule would have under-requested a measured class
    python3 trim_build_mem.py --apply      the mapping, then items.json rewritten (items.bak-<HHMM>Z.json first, then an atomic replace)

A Build's peak is its run's cgroup memory.peak (`kernel_memory_peak_bytes` in /workspace/jobs/runs/<run>/failure.json; the run is
<sweep>/<row>/two-task-build-run). The request is a Kueue request only: the dispatcher sets no memory limit, and nothing in the Build
reserves memory from it (`gpu-lease --mem-gb 0`).

A class is (model, TP, batch, tokens 256/32 or 1024/128, kind): greedy, stoch (the sampler at the default MAX_GATES) or stoch-1unit
(VERITY_QWORD_MAX_GATES raised: the sampler Call is one unit). P(class) is the largest peak measured in it. No unsubmitted class has
been measured, so each estimate starts from a measured class of the same model, TP and kind at a smaller shape and multiplies it by
the largest growth seen across models for each step between them:

    T(b)  256/32 -> 1024/128 at batch b (b >= 8 uses the factor measured at b = 8; it shrinks with batch: 3.7 at b1, 2.3 at b8)
    B     batch b -> 2b at 256/32 (8 -> 32 composed as 8 -> 16 -> 32), also used at 1024/128, where the batch growth measured
          (1 -> 8) is smaller than at 256/32
    S     stoch over greedy at the same shape, standing in for a stoch class with no measured base
    U     stoch-1unit 256/32 -> 1024/128 at batch 1

The estimate is the largest over the model's maximal measured bases; the new request is max(16, ceil(1.5 x estimate)), applied only
when it is lower than the current one. A class with no base (TP2, gemma2, qwen3-30b's stoch-1unit) keeps its request.
"""
import collections
import json
import math
import os
import re
import sys
import time
from pathlib import Path

FEED = Path("/workspace/jobs/gm-feed")
COV = Path("/workspace/jobs/cov")
RUNS = Path("/workspace/jobs/runs")
LOG = Path("/workspace/jobs/dispatch/log.jsonl")
SHAPE = re.compile(r"__tp(\d+)__b(\d+)__i(\d+)__o(\d+)__")
HEADROOM, FLOOR = 1.5, 16
BATCHES = (1, 8, 16, 32)


def peak_gb(it):
    f = COV / it["key"] / it["item"]["env"]["ROW"] / "two-task-build-run"
    if not f.exists():
        return None
    for name in ("failure.json", "status.json", "result.json"):
        p = RUNS / f.read_text().strip() / name
        if p.exists():
            m = re.search(r'"kernel_memory_peak_bytes": *([0-9]+)', p.read_text(errors="replace"))
            if m:
                return int(m.group(1)) / 1e9
    return None


def cls(it):
    env = it["item"]["env"]
    tp, b, i, o = map(int, SHAPE.search(env["ROW"]).groups())
    kind = ("stoch-1unit" if env.get("VERITY_QWORD_MAX_GATES") else "stoch") if "__stoch-" in env["ROW"] else "greedy"
    return (it["role"], tp, b, i, kind)


def ratios(P, a, b):
    """Largest P[(m, tp, *b)] / P[(m, tp, *a)] over the models with both measured, else None."""
    rs = [P[(m, tp, *b)] / P[(m, tp, *a)] for (m, tp, *rest) in P if tuple(rest) == a and (m, tp, *b) in P]
    return max(rs) if rs else None


def factors(P):
    """The growth factors, each the largest across models."""
    g = lambda a, b: max(ratios(P, (*a, k), (*b, k)) or 0 for k in ("greedy", "stoch"))  # noqa: E731
    return {"T1": g((1, 256), (1, 1024)), "T8": g((8, 256), (8, 1024)), "B1-8": g((1, 256), (8, 256)),
            "B8-16": g((8, 256), (16, 256)), "B16-32": g((16, 256), (32, 256)),
            "S": max(ratios(P, (b, t, "greedy"), (b, t, "stoch")) or 0 for b in BATCHES for t in (256, 1024)),
            "U": ratios(P, (1, 256, "stoch-1unit"), (1, 1024, "stoch-1unit")) or 0}


def estimate(c, P, F):
    """(estimate GB, the base it came from) for class c, or (None, why)."""
    m, tp, b, tok, kind = c
    if c in P:
        return P[c], "measured"
    step = {(1, 8): F["B1-8"], (8, 16): F["B8-16"], (16, 32): F["B16-32"]}
    cands = []
    for (m2, tp2, b2, tok2, k2), p in P.items():
        if (m2, tp2) != (m, tp) or b2 > b or tok2 > tok:
            continue
        if k2 == kind:
            f = 1.0
        elif kind == "stoch" and k2 == "greedy" and (m, tp, b2, tok2, "stoch") not in P:
            f = F["S"]
        else:
            continue
        if kind == "stoch-1unit":
            if b2 != b or b != 1:
                continue
            f *= F["U"] if tok2 < tok else 1.0
        else:
            prev = b2
            for nxt in BATCHES:
                if b2 < nxt <= b:
                    f *= step[(prev, nxt)]
                    prev = nxt
            if tok2 < tok:
                f *= F["T1"] if b == 1 else F["T8"]
        cands.append((b2, tok2, p * f, f"b{b2}/{tok2}/{k2} {p:.1f} x {f:.2f}"))
    near = [x for x in cands if not any((y[0], y[1]) != (x[0], x[1]) and y[0] >= x[0] and y[1] >= x[1] for y in cands)]
    return max(near, key=lambda x: x[2])[2:] if near else (None, "no measured base")


def validate(P):
    """Leave one out: each measured class, hidden from the bases and the factors, estimated from the rest. A class whose measured peak
    exceeds max(16, 1.5 x estimate) is one this rule would have under-requested."""
    worst, n, over = [], 0, 0
    for c, p in sorted(P.items()):
        rest = {k: v for k, v in P.items() if k != c}
        e, why = estimate(c, rest, factors(rest))
        if e is None:
            continue
        req = max(FLOOR, math.ceil(HEADROOM * e))
        n += 1
        over += p > req
        worst.append((p / req, c, p, e, req, why))
    for r, c, p, e, req, why in sorted(worst, reverse=True)[:12]:
        print(f"  {r:4.2f}  {c[0]:<20} b{c[2]:<2} {c[3]:>4} {c[4]:<11} measured {p:5.1f} est {e:5.1f} request {req:>3} ({why})")
    print(f"leave-one-out: {n} measured classes with a base; measured peak above the trimmed request in {over}")
    return 0


def main():
    items = json.loads((FEED / "items.json").read_text())
    submitted = set(re.findall(r'"key": "vllm-epoch-run/(cov-gm\d{3})"', LOG.read_text()))
    P = {}
    for it in items:
        p = peak_gb(it)
        if p is not None:
            c = cls(it)
            P[c] = max(P.get(c, 0.0), p)
    F = factors(P)
    print("factors " + " ".join(f"{k}={v:.2f}" for k, v in F.items()))
    if "--validate" in sys.argv:
        return validate(P)

    def est(c):
        return estimate(c, P, F)

    by = collections.defaultdict(list)
    for it in items:
        by[cls(it)].append(it)
    changes, lines = {}, []
    for c in sorted(by, key=lambda c: (c[0], c[1], c[4], c[2], c[3])):
        open_items = [it for it in by[c] if it["key"] not in submitted]
        if not open_items:
            continue
        e, why = est(c)
        reqs = sorted({it["item"]["resources"]["build"]["memory"] for it in open_items})
        new = None if e is None else max(FLOOR, math.ceil(HEADROOM * e))
        apply = [it for it in open_items if new is not None and new < it["item"]["resources"]["build"]["memory"]]
        for it in apply:
            changes[it["key"]] = new
        verdict = (f"-> {new}" if apply else f"keep (1.5x estimate {new} >= request)" if new is not None else f"keep ({why})")
        lines.append(f"{c[0]:<20} tp{c[1]} b{c[2]:<2} {c[3]:>4} {c[4]:<11} n={len(open_items)} req {reqs} "
                     f"est {('%.1f' % e) if e is not None else '-':>5} ({why}) {verdict}")
    print("\n".join(lines))
    before = sum(it["item"]["resources"]["build"]["memory"] for it in items if it["key"] not in submitted)
    after = before - sum(it["item"]["resources"]["build"]["memory"] - changes[it["key"]] for it in items if it["key"] in changes)
    print(f"unsubmitted {sum(1 for it in items if it['key'] not in submitted)}: {len(changes)} trimmed; their Build requests "
          f"{before} GB -> {after} GB")
    if "--apply" not in sys.argv:
        return 0
    raw = (FEED / "items.json").read_text()
    stamp = time.strftime("%H%MZ", time.gmtime())
    (FEED / f"items.bak-{stamp}.json").write_text(raw)
    items = json.loads(raw)
    submitted = set(re.findall(r'"key": "vllm-epoch-run/(cov-gm\d{3})"', LOG.read_text()))
    n = 0
    for it in items:
        if it["key"] in changes and it["key"] not in submitted:
            it["item"]["resources"]["build"]["memory"] = changes[it["key"]]
            n += 1
    tmp = FEED / f".items.json.tmp-{os.getpid()}"
    tmp.write_text(json.dumps(items, indent=1) + "\n")
    os.replace(tmp, FEED / "items.json")
    print(f"applied {n} at {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}; backup items.bak-{stamp}.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
