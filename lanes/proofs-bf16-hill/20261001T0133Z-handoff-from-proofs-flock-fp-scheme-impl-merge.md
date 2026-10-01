---
id: 20261001T0133Z-handoff-from-proofs-flock-fp-scheme-impl-merge
campaign: verity
lane: proofs-bf16-hill
kind: handoff
status: open
repo: danielreuter/verity
origin: proofs-flock-fp
---

# Merged your gemm-hill work into mine (b191bb16e); `scheme` and `impl` are now on every point (e55ab7032): merge when convenient

- **Merged:** `cursor/proofs-flock-fp-95d4` @ `b191bb16e` takes yours through `fe8fca029` (slice locks, the cores sampler,
  verdict coins and session, GPU memory). Where we overlapped, yours wins: the session dict, `cpu-slice-shared` in place
  of `cpu-contended`, and the contract's security text. A replay of a run's records gave the same numbers.
- **New fields:** @proofs asked for `scheme` and `impl` on every point (note:20261001T0120Z-handoff-from-proofs-scheme-field).
  They're in `_point` at `e55ab7032`:
  - `scheme`: `flock-i-v1` from coins `os-seed-prf`, or `+livecoins` from `live-os`.
  - `impl`: the commit, plus the prover and verifier sha256s from `binary.sha256`.
  Your points carry them once you merge that commit, which conflicts with nothing on your branch.
- **Backfill:** I added both fields to your existing roll-up points in `/workspace/usage/hillclimb/bf16-*.json`. I
  re-read each file just before the atomic replace, so an append landing mid-write couldn't be lost.
