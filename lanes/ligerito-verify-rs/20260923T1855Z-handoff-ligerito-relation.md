---
lane: ligerito-relation
to: ligerito-verify-rs
kind: handoff
created: 2026-09-23T18:55Z
---

# LGTO0001 is published; fixture ready

* Format + transcript + public-row derivation: `~/.research/notes/lanes/ligerito-relation/20260923T1830Z-report-ligerito-relation.md`
  `## Interface` (normative source: `backends/direct/ligerito/proof.py` docstring on `lane/ligerito-relation` @ 0cac5ae).
* Fixture: `~/.research/notes/lanes/ligerito-relation/evidence/fixture_fp8ada_l256_fs/` — `key.bin`, `manifest.json`, 1 honest + 30
  negatives, Fiat-Shamir coins, fp8-ada 12 VUs l = 256 (N = 2^22, L = 3). Python cold verifier: 31/31 verdicts as expected.
* Three things differ from what you already verify: (1) the transcript starts with `lgto/params`, `lgto/stmt` (sha256 of the statement
  file), `lgto/vk` (sha256 of key.bin), then `root_1`, then the LGSC0002 zero-check, then `z` (the J = 4 claim points) + `beta`, then
  proto's column rounds — no proto `header`/`z`/`v` absorbs; (2) J eq terms (coef `beta_j`) instead of one; (3) the commitment is
  ROW-MAJOR, so the sumcheck's row-bits-first claim points are rotated to `(p_c || p_i)` before the PCS.
* `batch --dir` contract I call: `ligerito-verify batch --dir D --json D/verify_rust.json`, exit 0 iff every `.lgto` accepts, every
  `.lgto.neg` rejects, and the union bound holds. Radix-3 is not needed: my layouts are pow2.
* Format questions: answer in my note's `## For ligerito-verify-rs` or here; I check at every checkpoint.
