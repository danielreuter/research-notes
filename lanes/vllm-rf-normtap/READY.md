---
id: vllm-rf-normtap/ready
lane: vllm-rf-normtap
kind: ready
created: 2026-09-26T22:19Z
updated: 2026-09-27T09:24Z
---
# vllm-rf-normtap READY (5): the MufuEx2Ftz shift clamp (PR #137)

## MufuEx2Ftz shift clamp (PR #137, `cursor/vllm-fa2-model-ex2-shift-57d5` @ `7d8a11e4`, base main `928790af`)
Merge-ready handoff: `lanes/vllm-coordinator/20260927T0902Z-handoff-from-vllm-rf-normtap.md`, which includes the test diff.
- **The fix.** `fa2_model.cpp` `mufu_ex2_bits` treats a right shift of 24 or more as 0; before, a count of 64 or more was
  undefined and wrapped mod 64 on x86, for |x| < 2^-63. Every 0 < |x| < 2^-23 now reads T[0] = 1.0. The copies of the wrap follow:
  the numpy twin, SP1 `ftz.rs`, flock `ir_tail.rs` and `mufu_probe.cu`'s device model.
- **CPU run `r20260927-083954-0e10`.**
  - Over all 2^32 words, the C++ equals the twin, and SP1 and flock are digest-equal to it.
  - Main and the fix differ on exactly the 402,653,184 words with biased exponent 40..63.
  - `cargo test -p veritor-zk-common`: 136 passed.
  - Both new tests pass on the fix and fail on main.
  - #101 layer-0 census: no ex2 input in (0, 2^-63).
- **Gate (b)** `6d1c` / `9946`: +2 tests passed, 0 new failures.
- **Pod:** `vyv-rf-normtap-c4` (`c4pymranf1lyv7`), 08:38Z–09:00:08Z, about $0.35.
- **L40S** `r20260927-091756-2451` (approved 09:08Z):
  - `mufu_probe verify` against the pinned tables gives 0 ex2 and 0 rcp mismatches over all 2^32 inputs, both for the fix's
    clamp and for main's undefined shift, so the device clamps.
  - The L40S tables equal the pinned ones.
  - Every tiny landmark is 1.0 on the hardware.
  - Pods `vyv-rf-normtap-g6` (a failed first attempt: nvcc was not on PATH) and `g7`, about $0.19 together; both terminated.

---
# vllm-rf-normtap READY (4): FA3's per-iteration Check_inf as Attention_v4 (opt-in), and #102 re-merged with main

## FA3 Check_inf (PR #105, `cursor/vllm-rf-fa3-checkinf-57d5` @ `b0a12771`, stacked on #102)
Merge-ready handoff: `lanes/vllm-coordinator/20260927T0322Z-handoff-from-vllm-rf-normtap.md`.
- `registry/fa3_check_inf.py`: `AttnBlock_v4{..., CHECK}` (unguarded running max at FA3's unmasked iterations) and `AttentionHead_v4` /
  `Attention_v4{..., MASKED_FROM}` (the tile's `n_block_min_causal_local_mask`).  Opt-in: `TargetProfile.fa3_construction =
  "check-inf-per-iteration"`; the default binds `Attention_v2`, so nothing of record moves.  The switch to the record is root's (re-baseline).
- CPU `r20260927-025023-e706`: selector off = base on 7/7 records and 1,248 attention bindings; partition checker 0 recomputes at 20 FA3
  geometries; tests / lints rc 0.  Gate (b) `cb9e` / `52f5`: jdiff rc 0.
- H100 `r20260927-025855-18e5`: default `cddc93cf` OK; guarded under the new construction `e8dfd09d` OK, 20/20: 62,050 MS words = the new IR
  (edge rows included), 21,928 output heads = `Attention_v4`, 0 mismatches.

## #102 re-merged with main `3040ac1f` -> `64a4c3d3` (handoff `lanes/vllm-coordinator/20260927T0318Z-handoff-from-vllm-rf-normtap.md`)
- Both flag sets kept (README, config.py, pipeline/manifest.py); main touched no tap source, hidden_stream or guarded_max.
- `r20260927-030426-8dfa`: #101's manifest from the stored record Build, main vs merge: flag off byte-identical (`368283ad`), `--guarded-max`
  differs only by the MS lengthening; touched tests jdiff rc 0; lints rc 0.

## Pods, spend
CPU `g05p8jgued7ppr` 02:48Z-03:15:08Z (~$0.43), H100 `tgn7b3ndihxybn` 02:58Z-03:16:30Z (~$1.08); both terminated.  About $3.8 of $10 with #102.

---
# vllm-rf-normtap READY (3): the MS class (`max * scale` per key block), opt-in behind GUARDED_MAX_TAP

Branch `cursor/vllm-rf-ms-plane-57d5` @ `40ec2e13`, base main `84801045` (#95 merged), [PR #102](https://github.com/danielreuter/verity/pull/102)
(draft).  Merge-ready handoff: `lanes/vllm-coordinator/20260927T0228Z-handoff-from-vllm-rf-normtap.md`.  Finding, sent first:
`lanes/vllm-coordinator/20260927T0152Z-handoff-from-vllm-rf-normtap.md` (FA3's unmasked iterations skip the -inf guard the IR applies).

## Change
- The guarded FA2 / FA3 builds (now `VERITY_MAT_SRC=123`) append the MS class after FIN: per (slab, row, key block) the `max_scaled`
  register the block's exp2 FMAs read, at every visited block.  Default builds (59) are unchanged.
- Host: `StreamLayout(ms=True)`, sizing (Python and native tap buffers, a seventh compacted plane, the arena bound, X-03), the policy's
  `max_scaled_words` in the query header, and `with_ms`, which lengthens the stream identities (the flag-on manifest digest moves).  The
  Commit refuses a build whose MS class is not the manifest's.
- Property (f): every visited MS word = IR `F32MulFtz(GuardNegInfZero(row_max), scale_log2)`; the masked digest compares the six classes.

## Results (all runs PRESERVED on R2)
| check | run | result |
|---|---|---|
| FA2 exactness, L40S (softcap incl.) | `r20260927-012901-955c` | default `668baecb` OK; guarded `338c7caa` OK: 64/64, 12/12, 547,438 MS words = IR |
| FA3 exactness, H100 | `r20260927-012825-34ba` | default `b9d61818` OK; guarded `d8c5c7e2` `ok: false` from 40 MS words with row_max -inf only (accepted 0200Z) |
| #101 off | `r20260927-013003-0f64` | PASS; root `7adcef49` = record; manifest `90f81868` = base main's |
| #101 on | `r20260927-013003-0f64` | Commit PASS x2, root `fa38d70b`; 512 stream identities +MS; 242,688 `max_scaled` words; committed MS = IR |
| partition + strict word check | `r20260927-015707-2c04` | 0 violations, 0 recomputes; 242,688 = checker = policy = word check |
| gate (b) base `84801045` / head `40ec2e13` | `1737` / `9dbf` | lints rc 0; 32 / 32 F; jdiff rc 0, +9 tests pass |

## Pods, spend
The H100 `rl550thlwam3ui` ran 01:26Z-01:46:13Z and the L40S `kt6i7m2zu3jy61` 01:26Z-02:25:59Z; both terminated.  About $2.27 of $10.

## Next
FA3 `Check_inf` per iteration in the IR (0200Z): a new FA3 block Definition, opt-in, CPU first, an estimate before any H100.

---
# vllm-rf-normtap READY (2): the guarded-max tap, opt-in behind GUARDED_MAX_TAP

Branch `cursor/vllm-rf-guarded-max-57d5` @ `a43ed3b9`, base main `35e78c37`, [PR #95](https://github.com/danielreuter/verity/pull/95)
(draft).  Merge-ready handoff: `lanes/vllm-coordinator/20260927T0030Z-handoff-from-vllm-rf-normtap.md`.  Finding, sent first:
`lanes/vllm-coordinator/20260926T2329Z-handoff-from-vllm-rf-normtap.md`.

## Change
- The FA2 / FA3 tap builds with `VERITY_ROW_GUARD=1` (`pod_fa2_tap.sh FA2_TAP_ROW_GUARD=1`, `pod_fa3_tap.sh FA3_TAP_ROW_GUARD=1`) write
  `GuardNegInfZero(row_max)` into ROW word 3 at every key block after a row's first, and 0 at the first.
- The policy lives in the manifest's query header (`query/guarded_max.py`); the identities and manifest digest stay the record's.  The
  Commit refuses a tap build whose word 3 does not match the manifest.
- Off by default: the default builds' kernels and the stream bytes are unchanged.

## Results (all runs PRESERVED on R2)
| check | run | result |
|---|---|---|
| FA2 exactness, L40S (softcap incl.) | `r20260926-232759-8412` | default `1d5484b9` OK; guarded `d18f3f62` OK: 64/64, 12/12 negatives, 423,438 guard words |
| FA3 exactness, H100 | `r20260926-232600-e66f` | default `635dcd3d` OK; guarded `5c83bcfe` OK: 20/20, 10/10 negatives, 40,122 guard words |
| #101 tap off | `r20260926-232328-7713` | Build/Match/Commit PASS; Program, manifest and run root = record |
| #101 tap on | `r20260926-232328-7713` | Commit PASS, root `ae21ed2e…`; policy 97,280 guard words = the tap list |
| #101 committed bytes | `r20260927-000857-9e96` | step 0: 4,096 guard words, step 1: 64, all = IR guard; root reproduced; ROW word 2 = visit index |
| partition checker (trial merge) | `r20260926-232341-8c37` | #101 attention: 0 violations, 0 recomputes; 97,280 guards -> ROW word 3; softcap and FA3 clean |
| gate (b) base `35e78c37` / head `a43ed3b9` | `881f` / `f468` | lints rc 0; 31 / 32 F; +13 tests pass; the one new failure is a timing race (5/5 pass on both sides, `32fe`) |

## Found, not fixed
- `max * scale` (242,688 words on #101) is committed by the cut and carried by nothing: ROW word 2 is the visit index.
- TP rows and the H100 rows (FA3 at kernel level only) are not covered.

## Pods, spend
The H100 `hzvx9w6liqxmc4` ran ~22:52Z-23:27:44Z, and the L40S `wqd4c5luh2x8ig` 23:18Z-00:32:08Z.  Two community L40S (driver 550, no CUDA
for torch cu129) were terminated after ~22 and ~2 min.  Spend was about $3.73 of $12.

---
# vllm-rf-normtap READY (1): norm-scale taps (PR #90, merged into main 35e78c37)

Branch `cursor/vllm-rf-normtap-57d5` @ `14ea93c6`.  Handoff `lanes/vllm-coordinator/20260926T2219Z-handoff-from-vllm-rf-normtap.md`.
- Exactness `abcd3320`: 62/62 kernel cases plus the source check.
- #101 tap off = record; tap on: 9,471 norm-scale words = plan.
- Partition checker norms 19/19, 0 recomputed.
- Gate (b) jdiff rc 0.
- Pod `yqvagba5ef4ckg` 20:28Z-22:17:54Z, about $2.00.
