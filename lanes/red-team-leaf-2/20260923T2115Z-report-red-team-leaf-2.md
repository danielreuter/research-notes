---
lane: red-team-leaf-2
kind: report
created: 2026-09-23T21:15Z
status: superseded
---

CHECKPOINT 0b40ae8a (05:54Z) [superseded] closed by coordinator 2026-09-25 05:55Z for the cloud switch-over: no sign of life >24 h; branch lane/red-team-leaf-2 pushed to origin; uncommitted work (if any) saved in evidence/uncommitted-0554Z*
CHECKPOINT 1054caf (21:10Z) [open] G1 reproduced: Ajtai check_system_key (F6) is a pattern scan; B=0 chain + decoy key rows ACCEPTED by Rust --allow-any-system (all digests 0); pinned mode refuses (PINS empty). F5/F8 labels OK. Next: share-logup pair negatives on CPU
CHECKPOINT 1054caf (21:00Z) [open] started; worktree on lane/red-team-leaf-2 @ 1054caf; reading share-logup/ajtai/blake3 landed code
# red-team-leaf-2 — adversarial re-check of the landed leaf code (share-logup 1054caf, ajtai-leaf d40399f, blake3-leaf 30abee8, leaf-iface 720820d) and the `-2` successors

Worktree `~/projects/verity-main-wt/red-team-leaf-2` on `lane/red-team-leaf-2` @ 1054caf (share-logup tip). No pod, laptop CPU only.
Question: can a prover make the verifier accept a statement whose operand rows do not hash to the committed roots; do the privacy
notes state the real leakage. Findings numbered G1.. (severity BREAK / BLOCKING / NIT); predecessor items F5–F8 + blake3 role re-checked.

## Log
* 21:00Z start; predecessor FINAL (red-team-leaf 17:55Z), leaf-campaign brief §0/§2/§3/§9, relaunch brief, predecessor lane reports and
  18:00Z handoffs read. Successor branches `lane/{share-logup,ajtai-leaf,blake3-leaf}-2` still at the predecessor tips at 21:00Z.
* 21:05Z share-logup 1054caf Rust pair path read (`verify.rs::verify_pair`, `gate_shared`, `format.rs::PairStatement::parse`,
  `auth.rs::check_hashed`, `relation.rs::by_digests`) + Python `SharedHashedRunner.prove_vus/verify_vus`, bench/live wiring.
  ajtai-leaf-2 landed 907fbc7 (key block per role, B = n x 512); read its `leaf.rs::check_system_key`.
* 21:10Z **G1 reproduced** (crafted negative `backends/direct/ligero/redteam/leaf2_ajtai_decoy.py` on `lane/red-team-leaf-2`, run
  against an export of 907fbc7 + its own release `ligero-verify`): a system whose real Ajtai chain uses B = 0 plus 2n decoy Linear
  rows carrying the derived key over 258 always-zero hint rows → Python accepts, **every committed digest is 0**, Rust
  `verify --allow-any-system` **ACCEPTS** (`system_pinned=false`); pinned mode refuses (no `PINS` row for ajtai at all). Control
  `--no-decoys` (naive B = 0): Rust refuses ("64 of the 64 Ajtai state rows do not carry the derived key B"). So F6 = PARTIAL.
* 21:25Z **share-logup pair through Rust**: crafted negatives `redteam/leaf2_share_pair.py` (CPU, fp8-ada 2x2 tile, 4 VUs, l = 256,
  `--soundness-bits 100`; binary built from 1054caf). FS 15/15 and interactive 17/17 as expected, every verdict with
  `system_pinned=true` (the CPU-built G/H systems hit the pod-built pins): honest A/B accept; systems swapped / G as both sides;
  H of pair B into pair A and G of B against A's H (`H: column challenge mismatch`); F_G[0][x][0]+1; VU 0 claims another x rank;
  unit digest +1; x/W digests swapped; unit role flipped (`unit roles do not match the authentication block`); relation string
  `fp8-ada+blake3`; H hashing a flipped row; H on rho+1 / rho = 1; `--coins-h` = G's coins (`H: coins are not this verifier's`);
  no X.hcoins → accepted but labelled "coins replayed" (correct). The lane had NO Rust pair negatives committed (only the
  Python gate on the pod), so this is new evidence, and the file is meant to be added to their tests.
* 21:30Z **G3** (live + shared): `bench_relation_vu` with `--verifier` hands `prove_vus` only G's live coins; `prove_vus` samples
  `coins_h` locally (relchain.py:730-732); the dump then writes those prover-sampled coins as `X.hcoins` (1581-1584), which the
  Rust batch treats as the verifier's own ("coins are this verifier's step-0 coins"). Today the path crashes before any proof is
  sent (`BenchLive.proved` → `proof_bytes(SharedProof)` has no `.auth`; the HELLO carries `system_bytes(R.sys)` = G only), so
  nothing is mislabelled yet, but there is no guard and the obvious fix (send `.g` + `.h`) leaves H's column challenge
  prover-known before H's root: H forgeable → shared rows need not hash to the committed roots. BLOCKING for any live/device-wave
  use of `included-hash-shared`; owner share-logup-2 (+ live-2b).
