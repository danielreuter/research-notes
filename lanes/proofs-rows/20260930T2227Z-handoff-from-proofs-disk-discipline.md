---
id: 20260930T2227Z-handoff-from-proofs-disk-discipline
campaign: verity
lane: proofs-rows
kind: handoff
status: open
repo: danielreuter/verity
origin: proofs (bc-8416bc72, Slack @proofs)
---

# Urgent, 3:27 PM PDT: node 1's disk is at 77% and grows about 190 GB/h; write no second copy of any circuit

Infra (Slack thread `1790807092.059919`): `/workspace` on node 1 hits the 85% hard stop at about 5:55 PM PDT, which halts
Builds and Commits. `flock-sweep2/stage-cache` (163 GB) duplicates the `circuit.txt` files in `runs/*/out/classes/`.

For your stage/prove split and its one measurement chunk:
- **No new cache.** Stage into the run's own `out/`, or hardlink from `stage-cache` (same filesystem). Never copy a
  1.3–3.3 GB `circuit.txt` a second time.
- **Digests as outputs** (circuit sha256, proof digest, verdict). Delete `circuit.txt` once the run is verified and
  preserved.
- **Check `df -h /workspace` before you stage;** at 80% or more, stop and report instead.
- **Delete your own scratch** when the measurement is done. Report the GB you wrote and removed.
