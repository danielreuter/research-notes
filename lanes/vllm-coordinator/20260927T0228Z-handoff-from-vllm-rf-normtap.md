---
lane: vllm-coordinator
kind: handoff
from: vllm-rf-normtap (agent bc-12c2f2d9)
created: 2026-09-27T02:28Z
---
# Merge-ready: the MS class (`max * scale` per key block), PR #102 (`cursor/vllm-rf-ms-plane-57d5` @ `40ec2e13`)

**Merge request.** Branch `cursor/vllm-rf-ms-plane-57d5`, head `40ec2e13`, base main `84801045` (the #95 merge).
[PR #102](https://github.com/danielreuter/verity/pull/102) is a draft. All pods are terminated. Spend: about $2.27 of the $10 cap: the H100 ran 01:26Z-01:46:13Z (~20 min at $3.49/h, ~$1.18), and the L40S ran 01:26Z-02:25:59Z (~60 min at $1.09/h, ~$1.09).

## What it adds (opt-in: the same `GUARDED_MAX_TAP=1` as #95)
- **Kernels.** A seventh stream class, `MS`, appended after FIN: one f32 per (slab, row, key block), source bit 64. The value is the
  `max_scaled` register the block's exp2 FMAs read, not a recomputed product. It is stored at every visited block, the first and the
  single-visible-key blocks included.
  - FA2: `apply_v8.py` step 6. `softmax.h` gets `scale_apply_exp2_ms`, which is the pinned `scale_apply_exp2` with the same arithmetic
    (the `UNFUSE_FMA` branch included) plus `Softmax::tap_max_scaled`. The mode-3 `VERITY_TAP_P` stores it (`Verity_mat_ctx::ms`).
  - FA3: `apply_fa3_tap.py` steps 2b / 3b, likewise in hopper `softmax.h`, stored at the mainloop's P site (`VERITY_FA3_MS`).
  - All of it is compiled only with `VERITY_MAT_SRC & 64`. The guarded builds (`FA2_TAP_ROW_GUARD=1`, `FA3_TAP_ROW_GUARD=1`) now
    compile `VERITY_MAT_SRC=123`. The default builds (59) do not have it.
- **Layout.** `hidden_stream.StreamLayout(ms=True)`: MS offsets, `word_index("MS", ...)` and `unrank`. The layout digest says `ms` only
  when it is set.
- **Host sizing.**
  - `hidden_source.mat_total_words(..., ms)`, the Python tap buffers, and the native `Fa2Wrap` / `Fa3Wrap`. On the compacted B>=2
    path, MS is a seventh per-sequence plane, and the X-03 plane classes expect it.
  - The arena bound gets the MS words through `extra_step_bytes`.
  - The host learns a build has MS from `verity_tap_src() & 64`.
- **The policy.** `query/guarded_max.py`:
  - `max_scaled_words`: per attention Call, NH x the blocks with more than one visible key (a one-key block's single exp2 unit absorbs
    it).
  - The query header states it beside the guard count (`guarded_max.max_scaled`).
  - `with_ms` lengthens every attention hidden-stream identity by HB x M x NB words, so the flag-on manifest digest moves.
    `manifest build` / `build-global --guarded-max` and `manifest-verify` (through the rebuild) apply it.
- **The Commit** refuses a tap build whose MS class does not match the manifest (`require_row3`, in both directions). #95's guarded
  build (src 59) is refused under the policy.
- **Exactness property (f).** Every visited MS word must equal the IR's `F32MulFtz_v1(GuardNegInfZero_v1(row_max), scale_log2)`, where
  row_max is the entry's ROW word 0, the running max after the block. The twin checks every word, and the reference evaluator checks a
  sample that includes every special row_max. The masked digest compares the six classes with the default build's record. Closedness
  covers MS.

## Exactness
| backend | run | default build | guarded build (row3 + MS) |
|---|---|---|---|
| FA2, L40S sm_89 (hd 64/96/128/256; 28 softcap cases) | `r20260927-012901-955c` | OK `668baecb…`: 64 cases, 12 negatives | **OK** `338c7caa…`: 64/64, 12/12; 547,438 MS words = IR (4,109 on the reference); 423,438 guard words |
| FA3, H100 sm_90 (hd 64/128) | `r20260927-012825-34ba` | OK `b9d61818…`: 20 cases, 10 negatives | `ok: false` `d8c5c7e2…`: 18/20, 10/10; 62,050 MS words, **40 differ, all with row_max `0xFF800000`** |

- **In every case on both backends:**
  - out and lse are bit-identical to the installed kernel and to the tap-off launch;
  - the six classes equal the default build's (masked digest);
  - ROW word 3 is the IR guard;
  - nothing spills outside the layout, and no expected word is unwritten (MS included).
- **FA3's `ok: false`** comes from `ms_mismatch_neg_inf_max` alone: `edge_rows` hd 64 (16 of 684 words) and hd 128 (24 of 556). The
  kernel stores `-inf` where the IR says 0, because FA3's unmasked iterations run `Check_inf = false`. The finding is
  `20260927T0152Z-handoff-from-vllm-rf-normtap.md`, and you accepted it on this basis (0200Z). The follow-up (FA3 `Check_inf` per
  iteration, opt-in) is mine next.
- Environment: torch 2.13.0+cu129, vLLM 0.28.1rc1.dev472+gd9105ea80, Triton 3.7.1.

## #101 (L40S, `r20260927-013003-0f64`)
- **Flag off:** Build, Match and Commit PASS.
  - The run root `7adcef49…1dec5` equals the record.
  - The manifest is `90f8186879d5…eaac` (7,043 identities). The base tree (main `84801045`) gives the same digest from the same Build
    (`r20260927-015707-2c04`), so the layout and manifest are unchanged.
  - The handoff's `368283ad…` is the record's older digest, which predates the relayout. vllm-rf-b4 found that no from-scratch Build
    gives it, and `90f81868` is also #95's flag-off digest.
- **Flag on:** two Commits, both PASS, with one run root `fa38d70b…b512`, never the record.
  - The manifest is `2c6a1cce…8766`, with 7,043 identities.
  - All 512 stream identities are lengthened by exactly their MS class, 309,760 words in total, and nothing else moved.
  - The query header states 97,280 guards and **242,688 `max_scaled` words**.
- **The committed bytes** (`--tensor-digests`, `VERITY_DUMP_STEP`, attention layer 0):
  - Step 0 (`g32x256x2`): 12,288 MS words, all equal to the IR (64 on the reference). 64 of them are single-visible-key blocks, so the
    cut uses 12,224. The 4,096 guard words are all the IR guard.
  - Step 1 (`g8x4x3`, the swapped decode): 96 MS words, all equal to the IR, and 64 guard words.

## Partition checker and strict word check (`r20260927-015707-2c04`, on the shipped tree)
- #101's attention: 4,592 Calls over 287 specializations, **0 violations, 0 recomputes**.
  - `F32MulFtz_v1` has **242,688** words, carried by the MS class. The checker's count equals the policy's.
  - `GuardNegInfZero_v1` has 97,280, carried by ROW word 3. The checker's count equals the policy's.
- The softcap (hd 256) and FA3 (hd 64/128) Definitions at T = 5, 129, 130 and 287: 0 violations and 0 recomputes, units of at most 32
  bits. Their `max_scaled` counts equal `NH x (blocks with NVIS > 1)`.
- One head, cut detail: cut OK and 0 recomputed gates, for FA2 hd 64 at T = 287 and 129, softcap at T = 130, and FA3 hd 128 at T = 287.
- **Strict word check** (`Q_word_v1{X=16,W=32,R=no-recompute}`, `strict=True`) on #101: ok, 0 violations.
  - Its `max_scaled` count is 242,688, equal to the policy's.
  - The flag-on manifest built with the strict word check is `2c6a1cce…`, the Commit's.
- Tests of the touched files: 208 passed, 1 failed. The failure was the X-03 policy record, which gained `ms: False` with the flag off.
  `40ec2e13` records `ms` only when it is set; gate (b) below runs on `40ec2e13`. Lints rc 0.

## Gate (b) (same L40S pod, git clones, GPU hidden from the tests)
| side | run | lints | gate (b) |
|---|---|---|---|
| base `84801045` | `r20260927-013032-1737` | rc 0 | 32 F / 3,938 P / 287 S / 6 xf (4,263) |
| head `40ec2e13` | `r20260927-020530-9dbf` | rc 0 | 32 F / 3,946 P / 286 S / 6 xf (4,270) |

- **jdiff rc 0**, with 0 new failures and 0 new skips.
  - 9 new tests, all pass. Two tests were renamed, and their renamed versions are among the 9.
  - One order-dependent test went from skip to pass (`test_weakref_death…`; it is on jdiff's unstable list).
- **The earlier head `06485b76`** (`r20260927-015718-23b6`) had one new failure: `test_x03_plane_classes::test_committer_derives…`. The
  policy record had gained `ms: False` with the flag off. `40ec2e13` fixes that, and its run above has no new failure.
- **Two failed starts of the head gate** (`r20260927-013014-f082`, `r20260927-014916-0f14`) exited 4 at the tree check. The #101 run,
  which ships the same tree, writes `integrations/vllm/out/` and a C++ build dir into it. `gate_b3.sh` and `ms_partition.sh` now leave
  shipped-only files out of that check.
- The GPU was hidden from the tests (`CUDA_VISIBLE_DEVICES=""`) and pytest-xdist was added, as in #95. Base and head ran on the same pod.
- Command: `research run --on vyv-rf-normtap-g5 --project verity --source <worktree @ sha> --cwd source --custody-r2 --env XDIST_ONLY=1
  --env NO_GPU=1 --send gate_b3.sh -- bash -c 'exec bash "$RESEARCH_RUN_DIR/inputs/gate_b3.sh" base|head2'`, then
  `baseline-jdiff.py gate_b-base.xml gate_b-head2.xml`.

## Behaviour changes (flag on only)
- A different run root.
- The manifest's stream identities are longer by the MS class, so its digest moves, and its query header gains
  `guarded_max.max_scaled`.
- The Commit needs the guarded build compiled with src 123, and refuses a mismatch in either direction.

## What deliberately did not change
- With the flag off:
  - the default builds' kernels, since the MS code is behind `VERITY_MAT_SRC & 64`;
  - the stream bytes, `StreamLayout` offsets and layout digest;
  - the manifest (`90f81868`, equal to base main's), the run root (#101 equals the record) and the X-03 records.
- `native_collect.py`, `padding_steps.py` and `native_host.py` stay at their P10 caps (line-neutral edits).
- The `_STREAM` tap-table labels and the plan doc are not edited; they belong to vllm-cross-call-check.

## Found, not fixed
- FA3's unmasked iterations skip the -inf guard. The IR should model it; see 0152Z, and the follow-up is mine.
- `_STREAM["F32MulFtz_v1"]` still says "ROW step (max * scale)". Under this policy the MS class carries it; the label is
  vllm-cross-call-check's.
- The TP rows, and the H100 rows at row level, are not covered, as with #95.

## Evidence
- Runs, all PRESERVED on R2:
  - H100 `vyv-rf-normtap-h2`: `r20260927-012825-34ba` (setup and FA3 exactness);
  - L40S `vyv-rf-normtap-g5`: `r20260927-012901-955c` (setup and FA2 exactness), `r20260927-013003-0f64` (#101),
    `r20260927-015707-2c04` (partition, word check, base manifest, tests, lints), `r20260927-013032-1737` (gate (b) base) and `r20260927-020530-9dbf` (gate (b) head `40ec2e13`). Also the earlier head's gate `r20260927-015718-23b6`, and the cancelled or failed starts `r20260927-013102-0c56`, `-013141-29df`, `-014905-df29` (wrong base sha, then the tree check) and `-013014-f082`, `-014916-0f14`.
- Notes: `lanes/vllm-rf-normtap/evidence/ms-plane/` (`fa2/`, `fa3/`, `row101/`, `partition/`, `gate-b/`) and `evidence/pod-scripts/`
  (`ms_exact.sh`, `ms_row101.sh`, `ms_partition.sh`, `gate_b3.sh`).
