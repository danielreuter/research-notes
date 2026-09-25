---
lane: ligero-steps-pin
kind: report
created: 2026-09-25T06:50Z
status: final
---

CHECKPOINT c8a16e2b (10:17Z) [final] x
CHECKPOINT c8a16e2b (10:15Z) [final] FINAL c8a16e2b: steps pin (H2, +shared Py gap) + R1/R2 cherry-picks + R4 fix; cargo 33+7+27, pytest 50 + regression 167 ok (1 pre-existing), 9/9 dumps, R2 T2 PASS, red-team harnesses refused. Pod terminated, ~$0.88.
CHECKPOINT c8a16e2b (09:48Z) [open] 09:48Z ready c8a16e2b sent. Disk notice ack: pulled only 228 KB of logs (art:61aedd27), deleted /tmp copy; nothing big. Regression r12 at ~163/171 (1 pre-existing live_test F). FINAL after it ends.
CHECKPOINT c8a16e2b (09:31Z) [open] 09:38Z READY handoff sent: c8a16e2b (steps pin + R1/R2/R4), art:61aedd27. 806a2f73 superseded by c8a16e2b (explained). Final pytest 50 passed; 9/9 dumps; R2 T2 PASS. Waiting on regression r12 (92/171) before FINAL.
CHECKPOINT 8e2f793c (09:03Z) [open] 09:07Z tip 8e2f793c. 9/9 dumps accepted w/ R1 (Rust pinned+Py). R2 recompute passes fp8-ada+poseidon2 T2 (4096 VUs); v6 shared fails closed. Red-team remap+orphan not reproduced, steps48 ok. R4 fix + reverify_test fix in. Regression running.
CHECKPOINT 06176b41 (08:41Z) [open] 08:47Z tip 06176b41: +R1/R2 (b-l-s-h cherry-picks) +R4 fix (reverify stmt/proof stems, batch n). cargo 33+7+27 ok. Pod: lsp-r12 (pytest/dumps/R2/regression) + lsp-rtsh (red-team remap/orphan/steps harnesses) running.
CHECKPOINT 1571143b (08:08Z) [open] steps_pin_test 34/34 at 1571143b (4 new +shared: honest ok; forged steps32, hdr steps32, hdr K768 refused Py+Rust; main's Py ACCEPTED hdr K768); 9 R2 dumps all accepted; regression 132 ok, 1 pre-existing live_test fail (same on main); rest running
CHECKPOINT 1571143b (07:36Z) [open] regression: 9 R2 dumps (fp8 bare/hash T2, bare-local x2, shared-local x2, blake3 x3) Rust pinned batch all accepted + Python 1st/last sub ok; before-fix comparison + regression pytest running
CHECKPOINT 1571143b (07:06Z) [open] cargo 32+7+27 ok on pod; steps_pin_test 33/34 (1 own-test bug fixed 1571143b); +shared forged steps32 / header steps32 / K768 refused Python+Rust; 9 R2 dumps fetched, reverify + regression pytest running
CHECKPOINT 236020a6 (06:50Z) [open] fix already on main (steps-pin c5cf7f6d/3781590e); audit found Python +shared v6 gap (no steps in SharedHashedRunner hooks, no v6 K check) -> 236020a6 pushed; pod setup running; next cargo+pytest+R2 regression

# ligero-steps-pin: red-team H2 (steps bound to nothing), shared code, Rust + Python

Worktree `~/projects/verity-main-wt/ligero-steps-pin`, branch `lane/ligero-steps-pin`, base main 25f0c1de. Pod
`vy-ligero-steps-pin` (cpu3c, 8 vCPU, $0.24/h).

## Finding at start: the fix is already on main

Lane `steps-pin` (report `lanes/steps-pin/20260923T2310Z-report-steps-pin.md`, tip f2a74128, merged by integration at
1703590a, ancestor of 25f0c1de) closed H1/H2 on 2026-09-23:

* Rust `c5cf7f6d` / `f2a74128`: `Relation.steps` / `Relation.k_ops` on every relation literal (`relation.rs`, next to
  `sys_id` / `table_digest` / `hashed_*` / `shared_systems`); `verify.rs::check_vu_shape`, called in `verify_core_inner`
  right after the system gate: bare K == `k_ops` (every mode), `steps <= leaf::max_steps` (Ajtai N, every mode incl.
  `--allow-any-system`), `steps == Relation.steps` (pinned), hashed K == 1536 (every mode). `leaf::PINS` entries
  (ajtai, blake3) key on the base `Relation`, so its `steps` applies to them.
* Python `3781590e`: `RelationHooks.steps` / `.max_steps`, `protocol.layout_error` at the top of `protocol.verify`
  (chain mode), `serialize.verify_files` v5 K check.
* Must-reject fixtures `backends/ligero-verify/fixtures/steps-pin/` (red-team collide pairs, n64 steps32, forged bare /
  +poseidon2 steps32) and tests (`tests/relations.rs` `steps_pin_*`, `steps_pin_test.py`).

Audit on 25f0c1de (after the later merges of +shared / blake3 / fp4):

| path | Rust | Python |
|---|---|---|
| bare v2/v3/v4 | check_vu_shape | layout_error (Relation.hooks.steps; vu.ChainRunner 96; FP4_HOOKS 24) |
| hashed v5 (+poseidon2, +blake3, +ajtai) | check_vu_shape | layout_error (HashedRelationRunner.hooks steps + max_steps) + verify_files K |
| +shared v6 pair | check_vu_shape on G and on H (`verify_pair_inner` -> `verify_core`), one header | **GAP**: `SharedHashedRunner.hooks` / `.hooks_h` built without `steps`; `verify_files` K check only for v5 (`_read_v6` dropped K) |

The +shared gap is the steps-pin lane's own integration note (`give hooks_h_for steps=rel.steps`, `verify_files` for
`st.v5 or st.v6`) that did not land at the merge.

## Fix (236020a6, Python only, additive; no digest / pin / Rust change)

* `relchain.SharedHashedRunner`: `hooks` and `hooks_h` carry `steps=rel.steps`.
* `serialize._read_v6`: keeps the header K (`row_words=K`); `verify_files` runs the shape + K == 1536 check for v6.
* `steps_pin_test.py`: honest fp8-ada 2x2 +shared pair (FS, ZK, CPU) accepted by Python and Rust (pinned); forged
  steps = 32 pair (honest prover, `K_VU` bumped); v6 header steps 32 and K 768; each refused by Python and by
  `$LIGERO_VERIFY` (G side's `check_vu_shape`) with the shape / K message.

## R1 / R2 / R4 (added by the coordinator 07:45Z; same handoff)

* Merge of origin/main 5631e667 (c733b7f4); R2 needs core `frame_v3`.
* R1: b-ligero-standard-hash 3af90e71 cherry-picked as 71905f0f. Reviewed: Rust `auth::layout_error` and Python
  `hashauth.layout_error` apply the same rule, x = W = vu for unshared trees and (vu // nb, vu % nb) for a tile; the
  tile convention matches `relchain.tile_indices`.
* R2: de2fa317 cherry-picked as 3e98dc55 (`reverify.commitment_problems` / `committed_trees`).
* R4 (red-team-standard-hash 08:35Z), fixed here:
  * 06176b41: `.stmt` stems == `.proof` stems == manifest entries; batch n == number of statements.
  * 24ab6c7d: hashed is decided from the pinned relation, and bare statements are not parsed (this fixed the 3
    reverify_test failures).
  * 943d5e96: v6 fails closed.
  * c8a16e2b: an unreadable statement is a problem; crossed or duplicate manifest entries are refused (this covers
    806a2f73's cases).
* Tests: `hashauth_test` has the red-team 2-VU remap end to end, plus the R2/R4 cases. `steps_pin_test` checks that a
  +shared pair fails closed.

## Results at c8a16e2b (art:61aedd2762f64fe16c5189c5378cab94dc86b221188922931a1fe85d307ad7b7)

* `cargo test --release`: 33 + 7 + 27 passed.
* `pytest hashauth_test reverify_test steps_pin_test`: 50 passed.
* Regression dumps: 9/9 accepted (Rust pinned batch + Python), unshared and tile alike.
* R2 over the dumps:
  * fp8-ada+poseidon2 T2 (4096 VUs) PASSES the recompute;
  * v6 shared-local dumps and hashed dumps without a `set` block fail closed.
* Red-team harnesses:
  * remap and orphan are not reproduced;
  * steps 48 is accepted, steps 64 is refused by both verifiers;
  * steps 32 cannot be built with blake3 (the gadget refuses 1-chunk rows).
* Earlier, at 1571143b: steps_pin_test 34/34; `leaf2_share_pair` 15/15 as expected; ligero regression 132 passed and 1
  pre-existing failure.

## Handoffs received

* coordinator 0745Z (add R1 + R2, one handoff, cap $8): done.
* b-ligero-standard-hash 0805Z (take 3af90e71 + de2fa317): taken; replied 0845Z.
* red-team-standard-hash 0835Z (R4): fixed in 06176b41 and follow-ups.
* b-ligero-standard-hash 0900Z (cherry-pick 806a2f73): superseded by 24ab6c7d + c8a16e2b; replied 0915Z.
* coordinator 0915Z (include 806a2f73): superseded, reason in the ready handoff.
* red-team-standard-hash 0920Z (24ab6c7d PASS): cited in the ready handoff; asked to re-run on c8a16e2b (0937Z).

## Log
* 06:29Z start; contract, red-team-leaf-3 report, ajtai-leaf-3 handoffs read; inbox empty.
* 06:35Z pod created. Found fix already on main (steps-pin lane); audit -> +shared Python gap.
* 06:47Z 236020a6 pushed; pod setup run lsp-setup launched.
* 07:06Z–08:08Z cargo, steps_pin_test and the 9-dump regression at 1571143b. The regression pytest stalled on conformance
  `[blake3]` (CPU), so I split it (regression_rest).
* 08:17Z–09:20Z R1/R2 integrated, then the R4 fix; pod runs lsp-r12, lsp-rtsh, lsp-final.
* 09:35Z ready handoff "steps pin + R1/R2 ready: c8a16e2b" sent to the coordinator.

## FINAL

tip: lane/ligero-steps-pin @ c8a16e2b (pushed; merged into main 3301c435 by the coordinator)
known-failures: live_test.py::test_shared_pair_every_coin_from_the_verifier[None] also fails on main (2^-99.86 < 2^-100); conformance [blake3] not run (CPU); reverify.py now fails +shared (v6) dumps and hashed dumps without a `set` block closed (by design)
pod: vy-ligero-steps-pin (7byyo9s4i8rh58, cpu3c, $0.24/h), 06:35Z-10:15Z, terminated; about $0.88 (cap $8); no laptop build, so no cargo clean needed
artifacts: art:61aedd2762f64fe16c5189c5378cab94dc86b221188922931a1fe85d307ad7b7 (all logs, JSON and pod scripts at c8a16e2b), art:e7b78840f270857bc54e82b53f659163a0df11e71e7c75a02a7884d89b60bea7 (regression list)

Delivered: the handoff `coordinator/20260925T0935Z-handoff-from-ligero-steps-pin.md`, "steps pin + R1/R2 ready: c8a16e2b",
with a 10:15Z addendum.
* H2: steps are pinned per relation. Rust `Relation.steps` + `check_vu_shape` were already on main. This lane closed
  the Python +shared (v6) gap: SharedHashedRunner hooks steps and the v6 K check.
* R1: auth layout rule, cherry-picked from b-ligero-standard-hash 3af90e71.
* R2: reverify recomputes the trees, cherry-picked from de2fa317.
* R4: stem / manifest / batch-n checks, hashed decided from the pinned relation, unreadable statements refused, v6 fails
  closed.

Evidence:
* `cargo test --release`: 33 + 7 + 27 passed.
* pytest focus: 50 passed.
* Regression list: 167 passed, 3 skipped, 1 known failure.
* 9/9 dumps re-verified (Rust pinned + Python).
* R2 recompute PASSES on the fp8-ada+poseidon2 T2 dump.
* The red-team remap / orphan / steps harnesses behave as expected.

Handoffs received, all acted on (see "Handoffs received" above): coordinator 0745Z, 0915Z and 0946Z (the disk notice:
only 228 KB of logs were pulled, then deleted); b-ligero-standard-hash 0805Z and 0900Z; red-team-standard-hash 0835Z and 0920Z.
