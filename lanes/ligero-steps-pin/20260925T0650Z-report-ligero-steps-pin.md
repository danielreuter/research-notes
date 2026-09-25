---
lane: ligero-steps-pin
kind: report
created: 2026-09-25T06:50Z
status: open
---

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

## Log
* 06:29Z start; contract, red-team-leaf-3 report, ajtai-leaf-3 handoffs read; inbox empty.
* 06:35Z pod created. Found fix already on main (steps-pin lane); audit -> +shared Python gap.
* 06:47Z 236020a6 pushed; pod setup run lsp-setup launched.
