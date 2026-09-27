---
lane: vllm-coordinator
kind: handoff
from: vllm-rf-normtap (agent bc-12c2f2d9)
created: 2026-09-27T00:30Z
---
# Merge-ready: the guarded-max tap, PR #95 (`cursor/vllm-rf-guarded-max-57d5` @ `a43ed3b9`)

**Merge request.** Branch `cursor/vllm-rf-guarded-max-57d5`, head `a43ed3b9`, base main `35e78c37` (which holds #86 and #90). It merges
cleanly into `cursor/no-recompute-partition-289b` `194ac3f9` (see the partition checker below).
[PR #95](https://github.com/danielreuter/verity/pull/95) is a draft.  All pods are terminated.  Spend is about $3.73 of the $12: the H100
~35 min at $3.49/h, the L40S ~74 min at $1.09/h, and two community L40S that could not run CUDA, ~23 min at $0.79/h.

## What it adds (opt-in: `GUARDED_MAX_TAP=1`, `CommitConfig.guarded_max_tap`, default 0)
- **Kernels.** FA2 `verity_tap.h` and FA3 `verity_tap_fa3.h`, `rowstat`: under `VERITY_ROW_GUARD=1`, ROW word 3 = `row_max != -inf ?
  row_max : 0` at every key block after a row's first (`step > 0`, the kernel's visit order), and 0 at the first.  The default builds are
  compiled without it and never write word 3.  `verity_tap_row3()` (0 / 1) says which build it is.
- **Builds.** `ops/pod_fa2_tap.sh FA2_TAP_ROW_GUARD=1` and `ops/pod_fa3_tap.sh FA3_TAP_ROW_GUARD=1` build `verity_fa2_matReqG.so` and
  `verity_fa3_matReqG.so` from the same trees, beside the default builds.
- **The policy.** `query/guarded_max.py`: `NH x (ceil(T/BN) - 1)` guarded maxes per attention Call.  It is a query-header statement
  (`manifest build --guarded-max`): the stream's identities, and so the manifest digest, stay the record's, and only word 3's bytes differ.
  manifest-verify compares the policy.
- **The Commit** refuses a tap build whose word 3 does not match the manifest (`hidden_source.require_row3` through
  `make_hidden_source(manifest=...)`).  `row_stages` picks the guarded build under the flag (`RunEnv.hidden_so_fa2_guarded` /
  `_fa3_guarded`) and moves aside a Build manifest whose policy differs from it.
- **Exactness property (e)** in `properties/fa_tap_exactness.py`: a guarded build is checked against the default build's record on the
  same GPU (`--baseline`).  Every stream word except ROW word 3 must equal the default build's (a masked digest).  Word 3 must be the IR's
  `GuardNegInfZero_v1` of the entry's row_max after a row's first block and 0 at the first (the twin on every word, the IR reference on a
  sample that includes every special value).  New edge cases give query rows -inf, +inf or NaN scores throughout, FA2's softcap included.
- `a43ed3b9` also fixes a latent crash in the Commit's diagnostic dump (`--tensor-digests` with `VERITY_DUMP_STEP`).

## Exactness (at `efb2bd4a`; the head adds only the dump fix, and the tap sources are those of `5425de64`)
| backend | run | default build | guarded build |
|---|---|---|---|
| FA2, L40S sm_89 (hd 64, 96, 128, 256; 28 softcap cases) | `r20260926-232759-8412` | OK `1d5484b9…`: 64 cases, 12 negatives | OK `d18f3f62…`: 64/64 cases, 12/12 negatives, 423,438 guard words |
| FA3, H100 sm_90 (hd 64, 128) | `r20260926-232600-e66f` | OK `635dcd3d…`: 20 cases, 10 negatives | OK `5c83bcfe…`: 20/20 cases, 10/10 negatives, 40,122 guard words |

In every guarded case:
- out and lse are bit-identical to the installed kernel and to the tap-off launch;
- every other stream word equals the default build's;
- every guard word is the IR guard of its row_max, and every first block is 0;
- the edge rows (-inf, +inf, NaN scores; FA2 softcap included) pass too.

Environment: torch 2.13.0+cu129, vLLM 0.28.1rc1.dev472+gd9105ea80, Triton 3.7.1.

## #101 (L40S, `r20260926-232328-7713`)
- **Tap off:** Build, Match and Commit PASS.  The Program `ccc213475e7c…00c6b`, manifest `90f8186879d5…eaac` (7,043 identities) and
  run root `7adcef491845…1dec5` equal the record.
- **Tap on:** Commit PASS.  The run root is `ae21ed2ee7b3…3308f`: new, never the record.  The manifest's identities are the record's; its
  query header states **97,280 guarded maxes, the tap list's 97,280**.  manifest-verify is OK with the policy on both sides.
- **The committed bytes** (`r20260927-000857-9e96`): the tap-on Commit ran twice more, with the Commit's `--tensor-digests` and
  `VERITY_DUMP_STEP` writing attention layer 0's stream at that step.  Both reruns reproduce the run root `ae21ed2e…`.
  - At step 0 (the prefill, `g32x256x2`): 4,096 guard words, each the IR's `GuardNegInfZero_v1` of its row_max (64 sampled by the
    reference evaluator), and every first block 0.
  - At step 1 (a decode, the swapped GQA launch `g8x4x3`): 64 guard words, with the same results.
  - ROW word 2 holds the visit index at every entry, which confirms the `max * scale` finding on committed data.

## Partition checker (`r20260926-232341-8c37`)
The checker (`Q_word_v1{X=16,W=32,R=no-recompute}`, `validate_unit_cut`) ran on a local trial merge `a3d4ec46` of
`cursor/no-recompute-partition-289b` (`194ac3f9`) and this branch (`ef734866`), never pushed.  Its tree is `678f436c`, which
`git merge-tree --write-tree 194ac3f9 ef734866` reproduces.
- **#101's attention.** 4,592 Calls over 287 specializations: 0 violations, 0 recompute violations.  The committed interior values and
  the stream fields that carry them:

| committed value | words (#101) | carried by |
|---|---|---|
| `MufuEx2Ftz_v1` (P f32, and the rescale) | 21,257,216 | P plane / ROW word 1 |
| `F2fpBf16_v1` (bf16 P) | 21,159,936 | RP plane |
| `AmpereBF16TcDot16_v1` (S) | 21,159,424 | S plane |
| `F32MulFtz_v1` (`max * scale`) | 242,688 | **nothing**: ROW word 2 is the kernel's visit index (the finding of 20260926T2329Z) |
| `Fa2InvSum_v1` | 146,944 | FIN word 1 |
| `GuardNegInfZero_v1` | **97,280** | **ROW word 3 (this tap)**; = the policy's count |
| `F32Max_v1` (row_max) | 96,256 | ROW word 0 |

- **Gemma's softcap attention** (hd 256, kBlockN 64) and **FA3's** (hd 64 and 128, kBlockN 128) at T = 5, 130 and 287: 0 violations and 0
  recomputes, units of at most 32 bits.  Their guard words equal `NH x (ceil(T/BN) - 1)`.
- **One head, cut detail** (FA2 hd 64 at T = 287 and 129, softcap hd 256 at T = 130, FA3 hd 128 at T = 287): cut OK, 0 recomputed gates,
  widths OK, every computed gate certified once, 0 redundant gates.
- **#101 whole Program** on the merged tree: `ok`, 0 violations.  The branch now counts the sampler's second `temperature == 0` inside its
  own unit as a redundant gate, not a recompute.  Merged-tree tests: 165 passed; lints rc 0.

## Gate (b) (same L40S pod, git clones, GPU hidden from the tests, pytest-xdist added)
| side | run | lints | gate (b) |
|---|---|---|---|
| base `35e78c37` | `r20260926-232633-881f` | rc 0 | 31 F / 3,913 P / 286 S / 6 xf (4,236) |
| head `a43ed3b9` | `r20260927-000916-f468` | rc 0 | 32 F / 3,925 P / 286 S / 6 xf (4,249) |

- jdiff: 13 new tests, all pass; 0 new skips.  One outcome changed: `tests.check.test_fork_pool::test_fork_pool_workers_die_with_a_sigkilled_parent`,
  which raised `ProcessLookupError` in the test's own `_alive(pid)`: the process exited between opening and reading `/proc/<pid>/stat`.
  The gate shared the pod with the #101 Commit reruns.
- **The fork-pool test is not a regression.** `r20260927-002905-32fe` ran that test file five times in each clone: 5/5 pass on base and
  5/5 on head.  This branch touches nothing it imports.
- The GPU is hidden (`CUDA_VISIBLE_DEVICES=""`, as on a CPU pod) because the GPU jobs shared the pod; base and head ran alike.
- Command: `research run --on vyv-rf-normtap-g4 --project verity --source <worktree @ sha> --cwd source --custody-r2 --env XDIST_ONLY=1
  --env NO_GPU=1 --send gate_b3.sh -- bash -c 'exec bash "$RESEARCH_RUN_DIR/inputs/gate_b3.sh" base|head'`, then
  `baseline-jdiff.py gate_b-base.xml gate_b-head.xml`.

## Behaviour changes (flag on only)
- A different run root.  The manifest's query header gains `guarded_max`, while its identities and digest are unchanged.
- The Commit loads the guarded build and refuses a mismatch in either direction.  manifest-verify also compares the policy.
- `row_stages` moves aside a Build manifest whose policy does not match the row's flag (`manifest.guarded-max-<0|1>-<stamp>.json`).

## What deliberately did not change
- With the flag off: the default builds' kernels (their only addition is the `verity_tap_row3` op, which returns 0), the stream bytes,
  identities, manifest, roots and verdict.  #101 equals the record.  The declaration and manifest-verify records gain keys only under the
  policy.
- No layout or buffer growth.  `pipeline/commit.py` stays at its P10 cap (line-neutral edits).  No epoch work.

## Found, not fixed
- **`max * scale` is not carried** (242,688 words on #101).  Detail and options are in `20260926T2329Z-handoff-from-vllm-rf-normtap.md`.
  With this tap, it is the attention cut's only uncommitted value.
- The no-recompute branch's `committed_today` maps `F32MulFtz_v1` to "ROW step"; it should say it has no field.  Its `_STREAM` also needs
  `GuardNegInfZero_v1` -> ROW word 3 once this merges.
- The TP rows (`AttentionTP2_v1` has no (T, NH) statics; `attention_words` refuses it by name) and the H100 rows (FA3 is covered at the
  kernel level only) are not covered.
- Two community L40S hosts had driver 550.163 (CUDA 12.4), where torch 2.13+cu129 sees no CUDA.  I replaced them with a secure L40S (driver 580).

## Evidence
- Runs, all PRESERVED on R2:
  - H100: `r20260926-225324-54e0` (setup), `r20260926-231746-db4a` (first exactness run, rule bug), `r20260926-232600-e66f` (FA3 exactness);
  - L40S: `r20260926-232004-ee99` (setup and the first FA2 exactness run), `r20260926-232759-8412` (FA2 exactness),
    `r20260926-232328-7713` (#101), `r20260927-000857-9e96` (#101 committed bytes), `r20260926-232341-8c37` (partition checker),
    `r20260926-232633-881f` and `r20260927-000916-f468` (gate (b) base and head), `r20260927-002905-32fe` (the fork-pool reruns);
  - the community L40S: `r20260926-225442-c5cb` (its bootstrap found no CUDA).
- Notes: `lanes/vllm-rf-normtap/evidence/guarded-max/` (`fa2/`, `fa3/`, `row101/`, `partition/`, `gate-b/`) and `evidence/pod-scripts/`
  (`gm_*.sh`, `gate_b3.sh`).
