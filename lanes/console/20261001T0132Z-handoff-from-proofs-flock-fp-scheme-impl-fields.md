---
id: 20261001T0132Z-handoff-from-proofs-flock-fp-scheme-impl-fields
campaign: verity
lane: console
kind: handoff
status: open
repo: danielreuter/verity
origin: proofs-flock-fp
---

# Hillclimb points now carry `scheme` and `impl` (verity/hillclimb-point/v0, additive)

Requested in note:20261001T0120Z-handoff-from-proofs-scheme-field, so the plots can tell protocol changes apart from
implementation changes. Both fields are set in `backends/flock/pod/gemm_hill.py` (`_point`), on `cursor/proofs-flock-fp-95d4`
@ `e55ab7032`:

- **`scheme`** (string): the proof-system scheme the point measured, derived from its `coins` field.
  - `"flock-i-v1"`: M0's configuration (SHA-512 Merkle, two Fast100 repetitions, `os-seed-prf` coins, the batched session,
    the tile layout).
  - `"flock-i-v1+livecoins"`: the same with fresh OS coins every round (`coins: live-os`).
  - `null`: a point with no timed session, so no coins recorded.
- **`impl`** (object): `{"commit": <tree commit>, "prover_sha256": <flock-circuit sha256>, "verifier_sha256": <the serve
  binary's sha256>}`. Today both are the one `flock-circuit` binary, so the two shas are equal.

**Backfilled:** every point already in `/workspace/usage/hillclimb/*.json` on vy-nebius-1, bf16-hill's included (27 points
across 16 files), now has `scheme: "flock-i-v1"`. Its `impl.commit` is the point's `commit` (12 characters), and its shas
come from its run's `out/binary.sha256`.

New points from proofs-flock-fp carry both fields from now on. proofs-bf16-hill's carry them once they merge `e55ab7032`.
