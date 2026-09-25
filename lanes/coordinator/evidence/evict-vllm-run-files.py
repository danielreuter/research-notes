"""Evict telemetry and log tarballs from FINISHED vLLM (vyv-*) runs that R2 has byte for byte (root approval, 2026-09-25 5:25 AM PT).

Candidates: runs whose remote.json machine starts with "vyv-" and whose status.json state is terminal; files named resources.jsonl
or *.tgz / *.tar.gz anywhere in the run dir, > 1 MB, unchanged (ctime) for 15 min. Each file is checked against R2
(objects/sha256/<sha256>, size + ETag) right before deletion and replaced by <name>.evicted (sha256, bytes, R2 key). Logged.
"""
import json, sys, time
from pathlib import Path

sys.path.insert(0, "/tmp/coord-evict")
from check import check, digests  # noqa: E402

RUNS = Path.home() / ".research/runs"
LOG = Path.home() / ".research/notes/lanes/coordinator/evidence/20260924T2120Z-eviction-log.tsv"
TERMINAL = {"done", "failed", "cancelled", "dead", "timed_out", "exited"}
MIN_BYTES, QUIET = 1 << 20, 15 * 60


def ts():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def load(p):
    try:
        return json.loads(p.read_text())
    except (OSError, ValueError):
        return {}


freed = n = kept = 0
with open(LOG, "a") as log:
    for run in sorted(RUNS.iterdir()):
        if not str(load(run / "remote.json").get("machine") or "").startswith("vyv-"):
            continue
        if str(load(run / "status.json").get("state") or "") not in TERMINAL:
            continue
        files = [f for f in run.rglob("*") if f.is_file() and not f.is_symlink()
                 and (f.name == "resources.jsonl" or f.name.endswith((".tgz", ".tar.gz")))]
        for f in files:
            st = f.stat()
            if st.st_size < MIN_BYTES or time.time() - st.st_ctime < QUIET:
                continue
            status, size, _ = check(f)
            if status != "OK":
                kept += 1
                log.write(f"{ts()}\tKEPT({status})\t{size}\t{f}\t-\n")
                continue
            sha, _ = digests(f)
            f.with_name(f.name + ".evicted").write_text(json.dumps(
                {"file": f.name, "sha256": sha, "bytes": size, "r2_key": f"objects/sha256/{sha}", "evicted_utc": ts(),
                 "approved_by": "root 2026-09-25 5:25 AM PT (vLLM finished-run telemetry/log tarballs)"}, indent=1))
            f.unlink()
            freed += size
            n += 1
            log.write(f"{ts()}\tdeleted-vllm-run-file\t{size}\t{f}\tobjects/sha256/{sha}\n")
    log.write(f"{ts()}\ttotal-freed-vllm-run-files\t{freed}\t{n} files, {kept} kept\t-\n")
print(f"freed {freed / (1 << 30):.2f} GiB, {n} files evicted, {kept} kept (not in R2)")
