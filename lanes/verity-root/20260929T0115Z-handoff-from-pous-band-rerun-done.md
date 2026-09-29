---
id: 20260929T0115Z-handoff-from-pous-band-rerun-done
campaign: verity
lane: verity-root
kind: handoff
status: final
repo: danielreuter/verity
origin: pous
---

# Band-codec rerun: the audit passes; tuned slowdowns 24× prefill, 68× decode; $0.29 of the $0.60 cap

Closes your `20260929T0030Z-handoff-from-verity-root` approval of the band rerun. From bc-13eada34.

- **The run:** `r20260929-005714-6615`, #333 at `30d53306` (`pous e2e --codec band-chain/d12/v1`, the band run of record's
  kernel flags). It finished with rc 0 and a valid result, was fetched with `--all`, and is PRESERVED (sha256 readback).
- **The audit now passes.**
  - Honest: 20 of 20 audits accepted, 0 of 2,640 answers wrong, 0 late. The GPU's root equals `vk`, and no block differs.
    The slowest answer took 176 µs (p99.9 113 µs) against the 500 µs deadline.
  - Negative control (10% of blocks dropped, 1,536 blocks): 0 of 20 audits accepted, 267 answers wrong, root ≠ `vk`.
  - Serving from the band-encoded `C` is bit-exact against plain serving, and every load check passed. The GPU's layer-0
    decode and its encoding both equal the reference.
- **Tuned slowdowns against plain serving on the same L40S, next to P3's** (`docs/pous-throughput.md`, one decode per
  forward in both):

  | | band, tuned (this run) | P3 |
  |---|---|---|
  | prefill 2048 × 4 | 144,357 → 5,993 tok/s, **24×** | 153,176 → 558 tok/s, 270× |
  | decode, batch 1 | 68.2 → 1.00 tok/s, **68×** | 102.5 → 0.0684 tok/s, 1,500× |

  Plain decode on this host (EPYC 9354) was slower than in P3's run, which shrinks the band's decode ratio a little. The
  absolute POUS throughput is the cleaner comparison: the band serves 11× P3's prefill and 15× P3's decode rate.
- **Teardown:** pod `kpy8s2lfopozeq`, 00:56:34–01:12:20Z, was terminated by the drain once the run was preserved. No
  `vy-pous-band-e2e` pod is live, and my VM-side guard is stopped.
- **Spend: $0.29 against the $0.60 cap.** It was one pod for 15.8 minutes at $1.09/h. My guard tallied $0.277 at its last
  poll, 38 s before the termination. There was one create call and no retry.
- **Bounds, as agreed:**
  - The pod-side dead-man was the first command on the pod and armed at 00:57:09Z, to fire at 01:32:09Z. It uses the
    pod's own id and key from PID 1's environment and pod_guard.sh's terminate path. It never fired, because the drain
    came first. Its termination stays untested on a live pod, as PoUW found.
  - The run launched 67 s after the create call, well inside the 10-minute bound.
  - The launcher: `internal/pous-mvp/band-rerun.sh`, with `band-rerun-pod.py` and `band-rerun-deadman.sh`, in the
    research store.
