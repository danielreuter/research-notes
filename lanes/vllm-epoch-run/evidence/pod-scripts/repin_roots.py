"""repin_roots.py EVIDENCE_DIR KNOWN_ROOTS RUN EPOCH_SHA [--write]: re-pin the canary positives' cc-8.9 roots from canary_pod.sh's evidence.

A positive is re-pinned only when all of these hold:
  * in pass a its only failure is the stale pin ("Build/Match/Commit green but run root ... != known-good ...") or it passed;
  * pass b ran it and gave the same root (reproduced), unless pass b was skipped for time (then it is reported, not pinned);
  * the negatives arena and omitted passed, and lateread's root differs from the new SmolLM2 root.
The previous root moves to `history` in the file's existing form ({cc, root, superseded_utc, why}).  Other compute capabilities and rows the
canary did not run keep their pins; they are listed.  Without --write it only reports.  Exit 0 when every positive is re-pinned."""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

POSITIVES = {"smollm2": "smollm2-135m__bf16__l40s__tp1__b1__i256__o32__mixed__greedy__bi-eager",
             "llama": "llama32-1b__bf16__l40s__tp1__b1__i256__o32__mixed__greedy__bi-eager"}
STALE = "Build/Match/Commit green but run root"
CC = "8.9"


def main() -> int:
    ev, kr_path, run, sha = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3], sys.argv[4]
    write = "--write" in sys.argv
    a = {c["check"]: c for c in json.loads((ev / f"epoch-{sha[:8]}-a.json").read_text())["checks"]}
    roots = json.loads((ev / "roots.json").read_text())
    kr = json.loads(kr_path.read_text())
    problems, pinned = [], {}
    for neg in ("neg_arena", "neg_omitted"):
        if (a.get(neg) or {}).get("result") != "PASS":
            problems.append(f"{neg}: {(a.get(neg) or {}).get('result')} {str((a.get(neg) or {}).get('detail'))[:160]}")
    for name, row in POSITIVES.items():
        c = a.get(name) or {}
        if c.get("result") != "PASS" and not str(c.get("detail", "")).startswith(STALE):
            problems.append(f"{name}: {c.get('result')} {str(c.get('detail'))[:160]}")
            continue
        r = roots.get(row) or {}
        if not r.get("a") or r["a"] == "-":
            problems.append(f"{name}: no run root in pass a")
        elif "b" not in r:
            problems.append(f"{name}: not reproduced (pass b skipped); new root {r['a'][:16]} not pinned")
        elif r["b"] != r["a"]:
            problems.append(f"{name}: pass b root {r['b'][:16]} != pass a {r['a'][:16]}")
        else:
            pinned[row] = r["a"]
    late = (roots.get("neg_lateread") or {}).get("a")
    smol = pinned.get(POSITIVES["smollm2"]) or (roots.get(POSITIVES["smollm2"]) or {}).get("a")
    if not late or late == "-" or late == smol:
        problems.append(f"neg_lateread: root {str(late)[:16]} does not differ from the new SmolLM2 root {str(smol)[:16]}")
    if problems:
        print("NOT RE-PINNED:\n  " + "\n  ".join(problems))
        return 1
    now = time.strftime("%Y-%m-%dT%H:%MZ", time.gmtime())
    for row, new in pinned.items():
        old = (kr["roots"].get(row) or {}).get(CC)
        if old and old != new:
            kr.setdefault("history", {}).setdefault(row, []).append(
                {"cc": CC, "root": old, "superseded_utc": now,
                 "why": f"pre-epoch root: the Q_word v1 re-baseline (S1-S4 at {sha[:8]}) moves what the collector binds; re-pinned from canary "
                        f"run {run} (pass a, reproduced in pass b)"})
        kr["roots"].setdefault(row, {})[CC] = new
        print(f"{row} {CC}: {str(old)[:16]} -> {new[:16]}")
    stale = sorted(f"{row} {cc}" for row, v in kr["roots"].items() for cc in v if not (row in pinned and cc == CC))
    print("kept (not reproduced by this canary): " + "; ".join(stale))
    if write:
        kr_path.write_text(json.dumps(kr, indent=1) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
