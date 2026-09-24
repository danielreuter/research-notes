"""For every recorded pod run that USES a Rust binary, find the latest recorded build of that crate on the same pod before
the run; report when the crate differs between the build commit and the run's recorded commit, and whether the run's outputs
are cited by the current renders."""
import json, re, subprocess
from collections import defaultdict
from pathlib import Path

A = Path.home() / ".research/store/attempts"
REPO = str(Path.home() / "projects/verity-main-wt/main")
CRATES = {"sp1": ["backends/sp1"], "ligero": ["backends/ligero-verify"],
          "gkr": ["backends/gkr/src", "backends/gkr/verifier", "backends/gkr/Cargo.toml", "backends/gkr/Cargo.lock"]}
USES = {"ligero": ("ligero-verify", "reverify"), "gkr": ("verity-gkr-verify", "/release/verity-gkr"),
        "sp1": ("veritor-zk-host", "sp1-bare", "VERITY_SP1_HOST", "tcdot", "sec128")}
BUILD_HINTS = ("pod_bootstrap.sh", "cargo ", "build.sh", "run_measure", "verifier_build")
R = Path.home() / ".research/notes/campaigns/afternoon/render"
cited = set()
for p in list(R.glob("22*Z-*.md")) + [Path("/tmp/coord-render/tables.md"), Path("/tmp/coord-render/drill.md")]:
    if p.exists():
        cited |= set(re.findall(r"art:([0-9a-f]{8})", p.read_text()))


def differ(a, b, k, cache={}):
    key = (a, b, k)
    if key not in cache:
        r = subprocess.run(["git", "-C", REPO, "diff", "--quiet", a, b, "--", *CRATES[k]], capture_output=True)
        cache[key] = {0: False, 1: True}.get(r.returncode)
    return cache[key]


runs = []
for f in sorted(A.glob("*.json")):
    try:
        a = json.loads(f.read_text())
    except ValueError:
        continue
    ex = a.get("execution") or {}
    rem = ex.get("remote") or {}
    pod = rem.get("pod_id")
    sha = rem.get("source_sha") or (a.get("source") or {}).get("commit")
    if not pod or not sha:
        continue
    text = " ".join(map(str, a.get("argv") or [])) + " " + str(ex.get("stage") or "") + " " + str(ex.get("cwd") or "")
    arts = {x[:8] for x in re.findall(r"([0-9a-f]{64})", json.dumps(a.get("outputs") or {}))}
    runs.append((ex.get("start_utc") or f.stem, f.stem, pod, ex.get("machine"), sha, text, arts))
runs.sort()
last_build = defaultdict(dict)
report = defaultdict(list)
for t, run, pod, machine, sha, text, arts in runs:
    is_build = any(h in text for h in BUILD_HINTS)
    low = text.lower()
    for k, hints in USES.items():
        if any(h in text for h in hints) and not is_build:
            b = last_build[pod].get(k)
            if not b and arts & cited:
                report[k + "-unrecorded-build"].append((run, machine, sha[:8], "-", "-", "no recorded build on this pod", sorted(arts & cited)))
            if b and b[0] != sha:
                d = differ(b[0], sha, k)
                if d is not False:
                    report[k].append((run, machine, sha[:8], b[0][:8], b[1], "DIFFERS" if d else "unknown", sorted(arts & cited)))
    if is_build:
        for k in CRATES:
            if k in low or (k == "sp1" and "veritor-zk-host" in text):
                last_build[pod][k] = (sha, run)
for k in list(CRATES) + [c + "-unrecorded-build" for c in CRATES]:
    rows = report.get(k, [])
    c = [r for r in rows if r[6]]
    print(f"{k}: {len(rows)} runs used a binary built from a commit whose crate differs from the run's; {len(c)} cited by current renders")
    from collections import Counter
    print('    by machine:', dict(Counter(str(r[1]) for r in c)))
