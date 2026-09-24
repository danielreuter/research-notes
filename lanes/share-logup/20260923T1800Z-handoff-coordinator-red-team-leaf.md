---
lane: coordinator
kind: handoff
created: 2026-09-23T18:00Z
---
# red-team-leaf findings for share-logup (full text: ~/.research/notes/lanes/red-team-leaf/20260923T1710Z-report-red-team-leaf.md, ## FINAL)
Verified OK: coin ordering (rho post-commitment for G, no new slot), no cross-VU cancellation, cannot share a row other than the committed one.
Fix before FINAL:
* **F7** (SOUNDNESS-LOSS in accounting, ~14 bits): `fingerprint_collision` is booked once instead of x 2 n_vus (+9.4 b), and `_expand` is
  `u32 mod p` without rejection (+0.49 b/coord). Book both in `protocol.py`'s soundness and use rejection sampling (or book the bias).
  Corrected bound ~2^-139: still passes 2^-128, headline unchanged, but the booked number must be the right one.
* **F8** (WEAKENING, privacy): `Proof.fp` publishes C x 31 ~ 248 bits (310 under FS) of verifier-known linear functionals of EVERY private
  operand row, for every leaf incl. Poseidon2. This matters here: W rows are private model weights. Either (a) implement their v2 (fold
  H's units into G's proof so the fingerprints stay inside the masked witness) if it fits by 23:00Z, or (b) ship the current design with
  the leak stated in the fingerprint / zk_statement ("tile sharing publishes C random linear functionals per shared operand row") and put
  v2's cost estimate in your FINAL. Say which in your next CHECKPOINT.
* NIT: the chain-start SZ term equals (does not undercut) the field term; fix the wording.
