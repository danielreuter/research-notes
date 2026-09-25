---
lane: verify-night-2
kind: handoff
from: b-ligero-sha256
cc: red-team-standard-hash, coordinator, b-ligero-standard-hash
---

# Verify the first SHA-256 full-relation cell: fp8-hopper-x4+sha256, 32768 VUs (sweep plateau), run at da74b03e

Producer: lane b-ligero-sha256, prover H100 80GB HBM3 (pod vy-b-ligero-sha256 = qmiq4rs1f0y4tr).

**Tree:** **da74b03e**, clean.
- The pod's source stamp is tree f73afc05, synced 09:48Z. The sweep started 09:55Z.
- da74b03e descends from main 3301c435 (steps pin + R1/R2/R4) and is in main 767115db, so it meets the red team's condition 1 (1033Z handoff).

**Bench:**
- Flags: `bench-vu --zk --mode interactive --auth included-hash --commit-per-rep`, l = 4096, p4, 5 reps; the sweep_vu plateau.
- Dump: rep 1, ligero-statement v5, `sha256/row/v1` leaves. The manifest carries the `set` block (32768 VUs, 97 proofs of 341 VUs, instances manifest fb444761…).

**Allocator:** lib.sh exported `MALLOC_MMAP_MAX_=0 MALLOC_TRIM_THRESHOLD_=1000000000000` for the run. The result predates 98d878ca, so it has no `software.allocator` field. The fingerprint's `commit` is null because the synced tree has no .git; the tree is the source stamp above.

| cell | bench-result | proofs (run-files/v1) | VUs | sub-batches | pinned system | attempt |
|---|---|---|---|---|---|---|
| fp8-hopper-x4+sha256 (sweep plateau) | art:4aa258eeba99ce7da2e2c43b9068530cab43c8f3e8907ebc59610e71db9cad84 | art:61842848ecbed86882d4f806bfbfb09bbb84634b040b5bfbc5c2892ec9a914d7 | 32768 | 97 | 6cf20505… (table 76c1ce7f…) | r20260925-095503-e592 |

**Numbers (producer's):**
- t.total 5.077 s plus commitment 0.240 s gives e2e 5.317 s, i.e. 6162 VU/s.
- e2e overhead vs native peak 1.045e8.
- Batch soundness 2^-128.07.
- 39.9 GB peak device memory, 7.1 GB transcript.

**Sweep points (VU/s):**

| VUs | VU/s | note |
| --- | --- | --- |
| 1024 | 4145 | |
| 2048 | 4739 | |
| 4096 | 5356 | |
| 8192 | 5860 | |
| 16384 | 5768 | |
| 32768 | 6162 | plateau |
| 65536 | 6112 | contended flag: the bench's own child GPU pids |
| 131072 | 6151 | contended flag: the bench's own child GPU pids |

The sweep stopped at "< 2% over two doublings".

**Producer check (not a verification label):**
- The pod's ligero-verify was built from da74b03e: 97/97 ACCEPT, 2^-128.07, system pinned, python agreement 97/97.
- Those results are in the proof tree (`rust_batch.json`, `rust_digest.json`, `verify_python.json`).

**Preservation:**
- Attempt, run record art:9475dd8e…, both artifacts and the other points: 13/13 PRESERVED on R2 (`research data push`, 11:47Z).
- The runner's own custody push failed with `RemoteDisconnected`. The objects were all on R2 already; the pod's store had lost 271 of the proof blobs, so the retries stalled re-fetching them.

**Verifier tree:**
- Use main 767115db (or lane da74b03e / 98d878ca) for `reverify.py` and `ligero-verify`, per red-team condition 2. Main before 767115db has no `sha256` scheme.
- 04 BOUND should read 2^-128.07, which meets condition 3.

**Not counted:**
- The be1a3bcb-era gates (art:c1351b8a, art:5b0162d6) and the 09:18Z/09:27Z screens: before da74b03e.
- The 09:49Z screen (art:8f340f20): a screen, not a cell.
- I won't re-run them; the e592 sweep replaces them.

**Next from this lane:** bf16-hopper-x4+sha256.
- PINS row b009fdc8 (sys a02f283d…, table 1b879d1a…), not yet in main.
- Gate r20260925-104053-b438: 13 honest sub-batches, 86 negatives, 0 failures.
- The re-sweep r20260925-113022-5a5f is running at b009fdc8. It will arrive as a second handoff; verifying it needs a ligero-verify with the b009fdc8 PINS row.
- The first bf16 sweep (6976, art:a8a1fc9f / proofs art:aeca551a, plateau 8192) is superseded: my custody work spoiled its 16384 point.
