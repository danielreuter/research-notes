"""Per pod: Rust builds recorded as research runs, in time order; flag any build of a commit whose committer time is older
than a commit already built on the same pod, where the Rust crates differ between the two commits."""
import json, subprocess
from collections import defaultdict
from pathlib import Path

A = Path.home() / ".research/store/attempts"
REPO = str(Path.home() / "projects/verity-main-wt/main")
CRATES = {"sp1": ["backends/sp1"], "ligero": ["backends/ligero-verify"], "gkr": ["backends/gkr/src", "backends/gkr/verifier",
          "backends/gkr/Cargo.toml", "backends/gkr/Cargo.lock"]}
BUILD_HINTS = ("pod_bootstrap.sh", "cargo ", "cargo\t", "build.sh", "run_measure", "SP1_HOST", "verifier_build")


def ctime(sha, cache={}):
    if sha not in cache:
        r = subprocess.run(["git", "-C", REPO, "show", "-s", "--format=%ct", sha], capture_output=True, text=True)
        cache[sha] = int(r.stdout.strip()) if r.returncode == 0 else None
    return cache[sha]


def crates_differ(a, b, kind):
    r = subprocess.run(["git", "-C", REPO, "diff", "--quiet", a, b, "--", *CRATES[kind]], capture_output=True)
    return r.returncode == 1


def kinds(text):
    k = set()
    if "sp1" in text or "SP1" in text or "veritor-zk-host" in text:
        k.add("sp1")
    if "ligero" in text:
        k.add("ligero")
    if "gkr" in text:
        k.add("gkr")
    return k


builds = defaultdict(list)
for f in sorted(A.glob("*.json")):
    try:
        a = json.loads(f.read_text())
    except ValueError:
        continue
    ex = a.get("execution") or {}
    rem = ex.get("remote") or {}
    pod, sha = rem.get("pod_id"), rem.get("source_sha") or (a.get("source") or {}).get("commit")
    if not pod or not sha or not rem.get("source_sha"):
        continue
    text = " ".join(map(str, a.get("argv") or [])) + " " + str(ex.get("stage") or "") + " " + str(ex.get("cwd") or "")
    if not any(h in text for h in BUILD_HINTS):
        continue
    builds[pod].append((ex.get("start_utc") or f.stem, f.stem, sha, ex.get("machine"), kinds(text), text[:160]))

flags = []
for pod, bs in builds.items():
    bs.sort()
    seen = {}  # kind -> (newest ctime, sha, run)
    for t, run, sha, machine, ks, text in bs:
        ct = ctime(sha)
        for k in ks:
            if k in seen and ct is not None and seen[k][0] is not None and ct < seen[k][0] and seen[k][1] != sha:
                if crates_differ(seen[k][1], sha, k):
                    flags.append((machine, pod, k, run, sha[:8], seen[k][2], seen[k][1][:8], text))
            if k not in seen or (ct or 0) > (seen[k][0] or 0):
                seen[k] = (ct, sha, run)
print(f"pods with recorded builds: {len(builds)}; build runs: {sum(len(v) for v in builds.values())}")
print(f"inversions where the crate differs: {len(flags)}")
for fl in flags:
    print("\t".join(map(str, fl)))
