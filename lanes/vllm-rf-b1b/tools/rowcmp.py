"""Compare one row's Commit at head and at base with the record and with each other.
usage: rowcmp.py ROW PROGRAM MANIFEST RUN_ROOT|- [SWEEP_ROOT=/workspace/cp]"""
import glob
import hashlib
import json
import os
import sys

row, program, manifest, run_root = sys.argv[1:5]
root = sys.argv[5] if len(sys.argv) > 5 else "/workspace/cp"
print("record program", program, "manifest", manifest, "run root", run_root)


def digest(x):
    return hashlib.sha256(json.dumps(x, sort_keys=True).encode()).hexdigest()[:16]


def replay_records(d):
    out = {}
    for p in sorted(glob.glob(f"{d}/**/sampled_replay*.json", recursive=True)):
        try:
            j = json.load(open(p))
        except Exception as e:
            out[os.path.relpath(p, d)] = {"error": repr(e)}
            continue
        sr = j.get("sampled_replay", j)
        if not isinstance(sr, dict):
            continue
        s = sr.get("sample") or {}
        pop = sr.get("population") or {}
        out[os.path.relpath(p, d)] = {
            "result": sr.get("result"), "grade": sr.get("grade"), "why": sr.get("why"),
            "seed": s.get("seed"), "seed_form": s.get("seed_form"), "picked": s.get("picked"), "evaluated": s.get("evaluated"),
            "equal": s.get("equal"), "mismatch_n": s.get("mismatch_n"), "not_evaluated_n": s.get("not_evaluated_n"),
            "picks": digest(s.get("picks_by_request_step")), "strata": digest(sr.get("strata")), "vus": pop.get("vus"),
            "by_family": digest(pop.get("by_family")), "not_evaluable": digest(pop.get("not_evaluable_codes")),
            "wall_s": (sr.get("timing") or {}).get("wall_s"), "workers": (sr.get("timing") or {}).get("workers"),
        }
    return out


arms = {}
for tag in ("head", "base"):
    d = f"{root}/sweep-{tag}/{row}"
    if not os.path.isdir(d):
        print(tag, "no row dir", d)
        continue
    def load(p):
        try:
            return json.load(open(p))
        except Exception:
            return {}
    v, top = load(f"{d}/commit/verdict.json"), load(f"{d}/verdict.json")
    rm = v.get("required_manifest") or {}
    checks = top.get("checks") or []
    arm = {"run_roots": v.get("run_roots") or top.get("run_roots"), "commit_pass": v.get("commit_pass"), "outcome": top.get("outcome"),
           "program": rm.get("program_digest") or top.get("program_digest"), "manifest": rm.get("manifest_digest") or top.get("manifest_digest"),
           "first_fail": v.get("first_fail_reason"),
           "checks": {c.get("name"): (c.get("status") or c.get("result") or c.get("outcome")) for c in checks if isinstance(c, dict)},
           "replay": replay_records(d)}
    arms[tag] = arm
    print(tag, json.dumps({k: arm[k] for k in ("run_roots", "commit_pass", "outcome", "program", "manifest", "first_fail")}))
    print(tag, "checks", json.dumps(arm["checks"], sort_keys=True))
    rr = arm["run_roots"] or []
    print(tag, "== record:", "program", str(arm["program"] or "").startswith(program), "manifest", str(arm["manifest"] or "").startswith(manifest),
          "run root", (run_root == "-") or (run_root in rr))
    for k, r in arm["replay"].items():
        print(tag, k, json.dumps(r, sort_keys=True))
if "head" in arms and "base" in arms:
    h, b = arms["head"], arms["base"]
    same = {k: h[k] == b[k] for k in ("run_roots", "commit_pass", "outcome", "program", "manifest", "first_fail", "checks")}
    print("head == base:", json.dumps(same))
    for k in sorted(set(h["replay"]) | set(b["replay"])):
        x, y = h["replay"].get(k), b["replay"].get(k)
        if x is None or y is None:
            print("replay", k, "only in", "base" if x is None else "head")
            continue
        diff = sorted(f for f in x if f not in ("wall_s", "workers") and x[f] != y.get(f))
        print("replay", k, "differs in" if diff else "identical (outside timing)", diff or "",
              "| wall_s base", y.get("wall_s"), "head", x.get("wall_s"))
