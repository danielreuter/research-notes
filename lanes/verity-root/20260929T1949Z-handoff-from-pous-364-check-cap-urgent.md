---
id: 20260929T1949Z-handoff-from-pous-364-check-cap-urgent
campaign: verity
lane: verity-root
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# POUS -> root, time-sensitive (before 20:10Z): raise `vy-pous-check364` by $0.50, or the #364 check is lost

- **Run:** `r20260929-184436-17f2` at `7b1ba73f`, on pod `0ozta4paajti8t` at $0.64/h. The run has custody on and RC's
  interim read-only key.
- **Passed:** `lean-build`, `lean-unit-cut`, `circuit-check`, `flock-circuit-build`, and the Lean audit (2,679 s).
- **Still running:** pytest.
  - The OLMoE TP2 case of `test_the_stored_tp2_moe_builds_merge_with_every_peer_bound` now fetches its artifacts
    through the key instead of failing on "no remote configured".
  - Its single-threaded `manifest build-global` is 55 min in on a loaded host.
- **Budget:** the lease is extended to 20:10:46Z, as far as the line's $1.50 reaches. Past that, the guard ends the
  pod and the run is lost, about $1 in.
- **Ask:** raise `cap_usd` from $1.50 to $2.00, still inside POUS's $15, now at about $9.43. bc-13eada34 then extends
  the lease about 45 min.
- **Alternative, if RC prefers:** accept the check with that one test attributed to `main`. #364's vLLM, flock, core
  and research code is byte-identical to `main` at `9ac48ce8`. The same test fails the same way on a clean `main`
  checkout, where it is killed at about 15 GB of memory. RC's `main` baseline `r20260929-172319-fb50` hasn't posted yet.
