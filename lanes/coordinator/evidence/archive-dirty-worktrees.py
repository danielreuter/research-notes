"""Archive closed lanes' dirty worktrees to R2, then remove them (user rule, 2026-09-25 1:56 AM PT).

Per worktree: tar.gz of the whole tree incl. uncommitted and untracked files, minus regenerable build dirs (EXCLUDE); check the
tarball lists every tracked, modified and untracked path outside EXCLUDE; `research data put --preserve`; re-verify the tarball
in R2 by direct hash (objects/sha256/<sha256>, size + ETag); only then `git worktree remove --force` (the branch is kept).
Any failed step skips that worktree's removal.  Every step is appended to worktree-archives.log.
Usage: archive-dirty-worktrees.py LANE [LANE ...]
"""
import fnmatch, json, subprocess, sys, tarfile, time
from pathlib import Path

sys.path.insert(0, "/tmp/coord-evict")
from check import check  # noqa: E402

HOME = Path.home()
WT = HOME / "projects/verity-main-wt"
MAIN = WT / "main"
RESEARCH = HOME / ".research/bin/research"
LOG = HOME / ".research/notes/lanes/coordinator/evidence/worktree-archives.log"
TMP = Path("/tmp/coord-archive")
EXCLUDE = ["target", ".rt-target", "__pycache__", ".venv", ".pytest_cache", ".mypy_cache", "node_modules", ".ruff_cache"]


def log(msg):
    line = f"{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())} {msg}"
    print(line, flush=True)
    with open(LOG, "a") as f:
        f.write(line + "\n")


def git(wt, *args):
    return subprocess.run(["git", "-C", str(wt), *args], capture_output=True, text=True, check=True).stdout


def excluded(rel: str) -> bool:
    return any(part in EXCLUDE for part in Path(rel).parts)


def expected_paths(wt: Path) -> set[str]:
    listed = git(wt, "ls-files", "-z", "--cached", "--others").split("\0")
    return {p for p in listed if p and not excluded(p) and (wt / p).is_file()}


def archive(lane: str) -> bool:
    wt = WT / lane
    if not wt.is_dir():
        log(f"SKIP {lane}: no worktree")
        return False
    branch = git(wt, "branch", "--show-current").strip()
    head = git(wt, "rev-parse", "HEAD").strip()
    dirty = [l for l in git(wt, "status", "--porcelain", "--untracked-files=all").splitlines() if l]
    git(MAIN, "fetch", "-q", "origin", branch)
    unpushed = git(wt, "rev-list", f"origin/{branch}..HEAD").split()
    log(f"START {lane}: {branch} @ {head[:8]}, {len(dirty)} dirty/untracked paths, {len(unpushed)} unpushed commits")

    TMP.mkdir(exist_ok=True)
    tgz = TMP / f"{lane}-worktree-{time.strftime('%Y%m%dT%H%MZ', time.gmtime())}.tar.gz"
    with tarfile.open(tgz, "w:gz") as tf:
        tf.add(wt, arcname=lane, filter=lambda ti: None if excluded(ti.name) else ti)
    with tarfile.open(tgz) as tf:
        names = {n.split("/", 1)[1] for n in tf.getnames() if "/" in n}
    missing = sorted(expected_paths(wt) - names)
    dirty_paths = [l[3:] for l in dirty]
    dirty_missing = [p for p in dirty_paths if not excluded(p) and p not in names]
    if missing or dirty_missing:
        log(f"FAIL {lane}: tarball missing {len(missing)} expected paths, {len(dirty_missing)} dirty paths: {(missing + dirty_missing)[:5]}")
        return False
    log(f"TAR {lane}: {tgz.name} {tgz.stat().st_size} B, {len(names)} entries, all tracked+modified+untracked paths present "
        f"(excluded: {','.join(EXCLUDE)})")

    meta = {"lane": lane, "branch": branch, "head": head, "dirty": dirty_paths, "unpushed_commits": unpushed,
            "excluded": EXCLUDE, "reason": "dirty closed-lane worktree archived before removal (disk)"}
    r = subprocess.run([str(RESEARCH), "data", "put", "--kind", "worktree-archive/v1", "--file", str(tgz), "--meta", json.dumps(meta),
                        "--preserve", "--json"], capture_output=True, text=True, stdin=subprocess.DEVNULL)
    if r.returncode != 0:
        log(f"FAIL {lane}: data put exit {r.returncode}: {(r.stderr or r.stdout).strip()[-300:]}")
        return False
    out = r.stdout.strip()
    try:
        art = json.loads(out)
        art_id = art.get("id") or art.get("artifact") or out[:80]
    except json.JSONDecodeError:
        art_id = out.splitlines()[-1][:120] if out else "?"
    log(f"PUT {lane}: {art_id} (--preserve OK)")

    status, size, _ = check(tgz)
    if status != "OK":
        log(f"FAIL {lane}: R2 direct-hash check {status}; worktree kept")
        return False
    log(f"VERIFIED {lane}: R2 objects/sha256 matches size {size} + ETag")

    subprocess.run(["git", "-C", str(MAIN), "worktree", "remove", "--force", str(wt)], check=True, capture_output=True)
    git(MAIN, "rev-parse", "--verify", f"refs/heads/{branch}")
    log(f"REMOVED {lane}: worktree {wt} (branch {branch} @ {head[:8]} kept; restore: git worktree add {wt} {branch} && "
        f"tar xzf $(research data fetch {art_id}) -C {WT})")
    tgz.unlink()
    return True


if __name__ == "__main__":
    ok = []
    for lane in sys.argv[1:]:
        if archive(lane):
            ok.append(lane)
        for stale in TMP.glob(f"{lane}-worktree-*.tar.gz"):
            stale.unlink()
    log(f"DONE {len(ok)}/{len(sys.argv) - 1} archived+removed: {' '.join(ok)}")
