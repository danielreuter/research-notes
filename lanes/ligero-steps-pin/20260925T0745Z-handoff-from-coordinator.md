---
lane: ligero-steps-pin
kind: handoff
from: coordinator
created: 2026-09-25T07:45Z
---

# ADD R1 + R2 (red-team SH FAIL, lanes/coordinator/20260925T0735Z-handoff-from-red-team-standard-hash.md) to your fix: same code, top priority

- R1 (BREAK): in `auth::check_hashed` (Rust) and `hashauth.verify_hash_auth` (Python) the (vu_index, x_index, w_index) triple is
  prover-chosen. Derive x/W from vu_index and the committed set's layout (unshared: x = W = vu; tile: from the verifier's expected
  (nx, nw)) and refuse any other; one negative with red-team's 2-VU fixture (Python ACCEPT, Rust PINNED ACCEPT today).
- R2 (BLOCKING): make independent re-verification recompute the a/b/y roots and the trees' `binding`
  (`hashauth.binding_digest(dataset, manifest, lo, hi, K, tree, schema)`) and `count` from the instance set by id and range, compare
  them to every statement's, and check that the sub-batches' vu_index cover the claimed range: in `reverify.py`, and/or
  `ligero-verify --expect-roots` so the Rust verifier refuses statement-described domains.
- Ship it together with the steps pin (H2) as ONE handoff "steps pin + R1/R2 ready: <sha>". Budget +$3 (cap $8). Every B-Ligero
  included-hash lane waits on this.
