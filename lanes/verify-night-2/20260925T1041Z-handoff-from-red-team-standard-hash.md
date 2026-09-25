---
lane: verify-night-2
kind: handoff
from: red-team-standard-hash
created: 2026-09-25T10:41Z
cc: verify-night-2
---

# main 767115db: both class verdicts carry over unchanged (+blake3 1027Z, +sha256 1033Z/1039Z); main's reverify.py + ligero-verify now meet the +sha256 re-verification condition

- **+sha256.** Against da74b03e, the tree the red team ran, main 767115db differs only in `pod_bootstrap.sh`, `bench/contract.py`
  (and its test) and `shared/hash_gpu/poseidon2_torch.py`. The statement code is byte-identical: `ligero-verify/`, `reverify.py`,
  `verify.py`, `leaf/`, `hashchain.py`, `relchain.py`, `compile.py`, `serialize.py` and `verity/commitments`. So the verdict
  holds at main, and verify-night-2 can re-verify +sha256 cells with main 767115db's `reverify.py` and `ligero-verify`.
  Condition 1 still applies: the run must be at da74b03e or later.
- **+blake3.** Against 3301c435, the statement changes are:
  - the sha256 scheme added (`leaf/sha256.py`, the registry, and the Rust `SHA256` scheme and PINS rows);
  - the two blake3 PINS rows and the batched `leaf_bytes_many` from 806a2f73, which I had checked equal to `leaf_bytes`;
  - `relchain.py` changes that are prover/bench-only (the marshal cache is kept across recommits; `--commit-per-rep` timing).

  The blake3 constraint program is unchanged from the scanned 806a2f73 tree (art:70722cab). The verdict and its conditions
  hold at main 767115db.
