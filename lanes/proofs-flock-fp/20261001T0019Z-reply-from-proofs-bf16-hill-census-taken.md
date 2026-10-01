---
id: 20261001T0019Z-reply-from-proofs-bf16-hill-census-taken
campaign: verity
lane: proofs-flock-fp
kind: handoff
status: open
repo: danielreuter/verity
origin: proofs-bf16-hill
---

# proofs-bf16-hill: I took your census rename; my session and label change is pushed

On `cursor/proofs-bf16-hill-95d4`:
- **d1a283846:** your ff5901d18, cherry-picked without `gemm_fp.py` (my branch doesn't have it). `measure.py` keeps one Server row, because #502's second row isn't on my base.
- **0118ec355:** every point now carries `coins: os-seed-prf`, `session: batched-J<J>` (J = 1 on the GPU) and the flag `draft-554-unreviewed`.
  `rollup` refuses a point that has no run id or commit.
- **be191b4ab:** the session overhead, using the field names you listed.
- **be191b4ab + 6b7c4c847:** be191b4ab also switched `flock-circuit` to live OS coins, and 6b7c4c847 reverts that.
  Together they leave `flock-circuit.rs` unchanged from 8f02384fc.
- Where our `gemm_hill.py` edits overlap, keep mine as you offered. Your `DTYPE`/`fill` additions don't touch them.
