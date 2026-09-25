"""Evict finished runs' telemetry (`resources.jsonl`) that is in R2 byte for byte (housekeeping rule: R2-verified by direct hash).

A file is evicted only if it is > 5 MB, untouched for 60 min, and objects/sha256/<sha256> on R2 matches its size and ETag
(the same `check` as the store eviction). It is replaced by `resources.jsonl.evicted` (sha256, bytes, R2 key) and logged.
"""
import json, sys, time
from pathlib import Path

sys.path.insert(0, "/tmp/coord-evict")
from check import check, digests  # noqa: E402

RUNS = Path.home() / ".research/runs"
LOG = Path.home() / ".research/notes/lanes/coordinator/evidence/20260924T2120Z-eviction-log.tsv"
MIN_BYTES, QUIET = 5 << 20, 60 * 60


def ts():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


freed = 0
with open(LOG, "a") as log:
    for p in sorted(RUNS.glob("*/resources.jsonl")):
        st = p.stat()
        if st.st_size < MIN_BYTES or time.time() - st.st_mtime < QUIET:
            continue
        status, size, _ = check(p)
        if status != "OK":
            log.write(f"{ts()}\tKEPT({status})\t{size}\t{p}\t-\n")
            continue
        sha, _ = digests(p)
        (p.parent / "resources.jsonl.evicted").write_text(json.dumps(
            {"file": "resources.jsonl", "sha256": sha, "bytes": size, "r2_key": f"objects/sha256/{sha}", "evicted_utc": ts()}, indent=1))
        p.unlink()
        freed += size
        log.write(f"{ts()}\tdeleted-run-telemetry\t{size}\t{p}\tobjects/sha256/{sha}\n")
    log.write(f"{ts()}\ttotal-freed-telemetry\t{freed}\t-\t-\n")
print(f"freed {freed / (1 << 30):.2f} GiB")
