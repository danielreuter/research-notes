---
lane: coordinator
kind: handoff
from: flock-backend
created: 2026-09-25T20:40Z
---

# flock-backend: please route the red-team-flock class review of verity/flock-pure-block/v2 (the Flock cell statement), plus a non-producer label for the H100 cell

**Review request (red-team-flock, class NON_ZK_PROOF at 2^-128 whole-proof; flock-128-r2 live coins):**
- Statement `verity/flock-pure-block/v2`: flock-gpu-link's `backends/flock/live/src/pure_block.rs` (PR #30 @ d3e96304; merged
  into cursor/flock-backend-4983, PR #34). One block R1CS per (VU, chunk): x and W chunk compressions (keyed BLAKE3) + the 32
  lowered units reading them; operand equality and the in-chunk accumulator chain as in-block copy rows; the 2 cross-chunk
  accumulators per VU are prover-committed publics opened by both adjacent blocks (v2); AccIn(v,0) = +0; key, counter, chunk
  CVs and the output word as public claims. Commit publics are checked natively (chunk CVs → keyed parents → the verifier's
  own row digests; outputs → its own y words) before any coin.
- What the verifier pins: the unit lowering `flock-unit-io/v1` (`backends/flock/python/verity_flock/lowering.py`, PINS
  bf16-hopper da1bbe2c…; `lower()` refuses any other bytes), the statement digest, Σ (relation, netlist sha256, statement
  digest, instance ref, frame-v3 roots a/b/y computed by the verifier from its own regenerated instance set
  `verity_flock/instances.py`), Fast100 × 2 reps on one root.
- Conditions to check: F1 (sessions with require_link and non-null link_sha256, verifier on a separate pod), F2 (production
  verifier pins the statement), F3; R1–R8 as in flock-live; the GPU prover's live hook (Flock-CUDA) and the sub-batch union
  bound (a 32,768-VU batch is 4 proofs; the cell's plateau is one 8,192-VU proof per timed run).
- Negatives to rerun: flock-pure-gpu `selftest` 18/18 (flock-gpu-link), plus my CPU `flock-pure selftest` for the
  operand/leaf/chain classes.

**Independent verification (rule 6):** the H100 cell's sessions were verified live by a separate same-DC CPU pod
(vy-flock-backend-ver), which I operate, so a non-producer label is still needed: e.g. replay the verifier pod's session
records + proofs (they are in its run's `out/verifier/p3-8192/sessions-s0/`) with `flock-pure-gpu` built from PR #30.
Run ids follow in my next checkpoint.
