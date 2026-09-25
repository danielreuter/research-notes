"""Preserve, then evict, finished vLLM (vyv-*) runs' telemetry and log tarballs that R2 lacks (root approval, 2026-09-25 5:25 AM PT:
evict only files R2 has byte for byte; the same preserve-then-evict pattern as the 2:47 AM PT orphan blobs).

Same candidates as evict-vllm-run-files.py. One file at a time: `research data put --kind orphan-run-file/v1 --preserve`, then the
direct R2 hash check, then delete the run file and the store's copy of the blob (so disk never holds more than one extra file),
refresh the catalog presence, and leave <name>.evicted (sha256, bytes, R2 key, holder artifact). Logged to the eviction log.
"""
import json, subprocess, sys, time
from pathlib import Path

sys.path.insert(0, "/tmp/coord-evict")
from check import check, digests  # noqa: E402

sys.path.insert(0, str(Path.home() / "projects/verity-main-wt/cli/tools/research/src"))
from research.store.local import LocalStore  # noqa: E402

RUNS = Path.home() / ".research/runs"
STORE = LocalStore(Path.home() / ".research/store")
RESEARCH = str(Path.home() / ".research/bin/research")
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


freed = n = failed = 0
with open(LOG, "a", buffering=1) as log:
    for run in sorted(RUNS.iterdir()):
        machine = str(load(run / "remote.json").get("machine") or "")
        if not machine.startswith("vyv-") or str(load(run / "status.json").get("state") or "") not in TERMINAL:
            continue
        for f in sorted(x for x in run.rglob("*") if x.is_file() and not x.is_symlink()
                        and (x.name == "resources.jsonl" or x.name.endswith((".tgz", ".tar.gz")))):
            st = f.stat()
            if st.st_size < MIN_BYTES or time.time() - st.st_ctime < QUIET:
                continue
            sha, _ = digests(f)
            art = None
            if check(f)[0] != "OK":
                meta = {"reason": "finished vLLM run file preserved before eviction (laptop disk)", "run": run.name,
                        "machine": machine, "path": str(f.relative_to(run)), "sha256": sha}
                r = subprocess.run([RESEARCH, "data", "put", "--kind", "orphan-run-file/v1", "--file", str(f), "--meta", json.dumps(meta),
                                    "--preserve", "--json"], capture_output=True, text=True, stdin=subprocess.DEVNULL)
                if r.returncode != 0:
                    failed += 1
                    log.write(f"{ts()}\tPUT-FAILED\t{st.st_size}\t{f}\t{(r.stderr or r.stdout).strip()[-160:]}\n")
                    continue
                art = next((w for w in r.stdout.replace('"', " ").split() if w.startswith("art:") and len(w) == 68), None)
            status, size, _ = check(f)
            if status != "OK":
                failed += 1
                log.write(f"{ts()}\tKEPT({status})\t{size}\t{f}\t-\n")
                continue
            f.with_name(f.name + ".evicted").write_text(json.dumps(
                {"file": f.name, "sha256": sha, "bytes": size, "r2_key": f"objects/sha256/{sha}", "holder": art, "evicted_utc": ts(),
                 "approved_by": "root 2026-09-25 5:25 AM PT (vLLM finished-run telemetry/log tarballs)"}, indent=1))
            f.unlink()
            blob = STORE.object_path(sha)
            if blob.is_file():
                blob.unlink()
                if art:
                    try:
                        STORE.index.set_presence(art, local=STORE.has_local(art))
                    except Exception as e:  # noqa: BLE001
                        log.write(f"{ts()}\tpresence-update-failed\t0\t{art}\t{e}\n")
            freed += size
            n += 1
            log.write(f"{ts()}\tdeleted-vllm-run-file\t{size}\t{f}\tobjects/sha256/{sha} (holder {art or 'pre-existing'})\n")
    log.write(f"{ts()}\ttotal-freed-vllm-preserved\t{freed}\t{n} files, {failed} failed\t-\n")
print(f"freed {freed / (1 << 30):.2f} GiB, {n} files, {failed} failed")
