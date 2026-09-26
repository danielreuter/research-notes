---
id: vllm-rf-epoch/ready
lane: vllm-rf-epoch
kind: ready
status: REVIEW (epoch, partial) -- owner review, not merge-ready
created: 2026-09-26T02:20Z
---
# vllm-rf-epoch READY: C3 identities + the re-baseline epoch (partial)

- **Branch:** `lane/vllm-rf-epoch` @ **`101e8917`** (pushed), on b4c `5494e29f` (= `5c05ff6d` + main `38a8d35d`). It lacks a5, b1,
  b4c's `9689a1ef` and main since `38a8d35d` (all digest-neutral by their gates). Merge main before landing; a pod running the
  merged tree needs `protocols/sampled_proofs` on PYTHONPATH (PR #29), or a bootstrap from main `541d31d3` or later.
- Agent bc-e66a058f. Brief `lane-briefs/vllm-epoch.md`; decisions `lanes/vllm-rf-epoch/20260925T{2030,2145}Z-handoff-from-vllm-coordinator.md`.

## Commits
| sha | item | kind | moves |
|---|---|---|---|
| `30427930` | 1. Programs cite core `AmpereBF16TcDot16_v2` (c2b `dedf5313` cherry-picked; subject relabelled) | epoch | Program digests of the Ampere rows, golden |
| `a784d421` | 2a/2b. `gpu_info()` drops `gpu.pod` (it's now in the header notes); `profile_manifest` raises instead of the `profile-fallback/v1` id. **Protected file** `engine/vllm_adapter.py`: hunks at `profile_manifest` (notes gains `pod`; the `except` block becomes `raise RuntimeError(...) from e`). P7 entry moved; P10 1913 -> 1906 | epoch, **owner review** | every row's profile id, so leaf ids and roots |
| `89cd9d1a` | 6. host admission lag = `global_program.workload_target(wl).lag()` (the import missed; broad except removed) + test | non-epoch, digest-neutral (no check reads `admission_*.json`; the declared lag is 1 = the old fallback on every row) | `admission_*.json` only |
| `73a9a90a` | 7. `research_tools.CLOSURE` + `packages/verity/src/verity/evaluation/**`; code_identity `54ed9053…` (1191 files) -> `e58416b9…` (1194) | epoch, key-only | tool ids / hot-Commit key / TP tree of record |
| `ad8050e9` | m32 `271a0952` cherry-picked (pre-gate sha): `scheme.chunk_header` passes `M & 0xFFFFFFFF` | non-epoch, digest-neutral | none |
| `14b321ad` | `rebaseline.py write` for #101 and #67 (digest checks only, `--force`) | epoch, **owner review** | `expected/` of 2 rows |
| `101e8917` | 5. golden corpus re-record: m1 `d2b299f5…` -> `d72cd7ad…`, m6 `14a3ac66…` -> `074e6cab…` (as c2b predicted; `--check` 2/2) | epoch, **owner review** (protected) | `corpus.json` |

**Deferred (larger than S):**
- 2c: the `sm89-eager` label from the probed capability. The κ id is fixed before any header is read.
- 3: the G1–G8 key names. There are two namespaces, ~30–40 files, and no agreed map.
- 4: the host `chunk-leaf-v1` label. `padding_steps` keys the padding leaf rule off the same label.

## Recording trees
Build+Match at `a784d421` (#67 at `89cd9d1a`); every Commit re-ran at `ad8050e9` (m32's **pre-gate** fix sha `271a0952`), over
those Builds. #101's Commit ran at `a784d421` (its M is below 2^32). The golden corpus was recorded at `a784d421`. Rebaseline
`run` (T0,T1,T2; the recorded rows as `VERITY_REGRESSION_CANDIDATE`, fixtures prefetched into the pod store) and `write` ran at
`ad8050e9`.

## Rows
| # | row | status | Program (request / build digest) | manifest | Commit | note |
|---|---|---|---|---|---|---|
| 101 | llama32-1b b1 stoch | **re-baselined** (digest checks) | `079ee0a8…` -> `dd206e6c…` | `368283ad…` -> `ee65240e…` | PASS | = c2b's epoch values |
| 67 | olmoe b32 | **re-baselined** (digest checks) | `a7be1df3…` -> `1a8b7eda…` | written | PASS (4962 s, tp70 GPU 0) | coverage FAIL (missing 20,928): finding |
| 4 | smollm2 b16 | not written | `262201f9…` | `990e2d1f…` | PASS, but expected FAIL | **finding**: the FAIL-class row's Commit now passes |
| 23 | llama32-1b b64 | not written | `2bdeb8e3…` | `e55e5407…` | NOT_RUN (rc 3) | **finding**: a GREEN row whose Match FAILs (NO FOLD) |
| 57 | gemma2-2b b8 | not written | `9020930a…` | `21a77237…` | FAIL (local_replay) | FAIL-class; coverage differs |
| 60 | mistral-7b b8 | not written | `b9ef8d2e…` | `c470c607…` | OOM (rc 137) with `VERITY_ADMIT_OVER_BOUND=1` at 119 GiB | memory |
| 70 | olmoe tp2 b8 | not written | ranks `508c0f77…`/`9c2554f1…` | — | FAIL (tp.commit pass False) | FAIL-class; most checks don't apply to the TP layout |
| 11, 39 | b1 i4096 o512 | not re-baselined | — | — | — | memory (planner: #39 Build 486 GiB) |
| 68 | olmoe b32 arrivals | not re-baselined | — | — | — | time (Build > 4.3 h) |
| 73 | qwen3-4b H100 | not re-baselined | `345ebaf9…` | `69598f76…` | OOM at 251 GB | memory |
| 74 | qwen3-4b-fp8 H100 | not re-baselined | — | — | — | time |
| 75 | qwen3-30b tp2 | not re-baselined | — | — | — | rank Build LP1024_T127 timed out at 7200 s |
Rows not written keep their old `expected/` (pre-epoch evidence).

`rebaseline.py table` over all 7 recorded rows: `notes-asset` `evidence/table.txt`; full `write --force --dry-run`:
`evidence/write-dryrun-all.txt` (lane dir). **The contracts were still the v1 reference**, so every diff is v1 -> v2 + epoch, not the
epoch alone: for example collector `+plan`, and #101's step segmentation (1 -> 32 steps, an accepted decision). The digest checks I wrote
carry both. Attributing them field by field to epoch items is the owner's review.

## Overnight goal 8: the dropped rows at `101e8917` (evidence, not written)
- #75: Build PASS 5530 s (BUILD_TIMEOUT 14400; ranks 8f72fe88…/cddba988…). Match: collective PASS (12,544 collectives, 0 mismatches),
  per-rank fold FAIL (FAIL-class). Commit FAIL, CUDA OOM at COMMIT_GPU_UTIL 0.80 after 5204 s. Run `r20260926-075240-af98`, copy
  `r20260926-120140-813e`.
- #68: Build PASS 9437 s (4ca0a9ef…, manifest 95888c8d…), Match PASS (fold True). Commit: see below. Run `r20260926-075702-d929`.
- #73: partial; stopped in Build (7 of 8 shapes) at 10:32Z so as to end by 12:30Z. Copy `r20260926-103153-80dd`.
- #23 GPU confirmation: Build PASS (2bdeb8e3, e55e5407), Match PASS (fold True), Commit OOM at 251 GB after 3435 s (the F-dA-15
  bound predicted 183 GB). Copy `r20260926-080221-afaa`.
- #11, #39: capacity gap (need >= 512 GB). #74: skipped.

## Findings (not fixed)
- M >= 2^32 header: c1's core `chunk_header` validation rejected the kernels' u32 M (fixed by m32, `ad8050e9`).
- `ops/row_pod.sh` has no TP hook, so the TP rows must call `tp_stage.sh` (my first #70/#75 runs were invalid, and were redone).
- Bisect (`lanes/vllm-coordinator/20260926T0335Z-handoff-from-vllm-rf-epoch.md`), no offending commit for either:
  - #4: the v1 FAIL class was a record-audit RED (descriptor.json.gz missing from the archived record); v1 never ran a Commit.
    Test expectation, so a class re-baseline is the owner's decision.
  - #23: the capture was SIGKILLed (-9) at moe67's 125 GB cgroup (planner: Match 148,303 MiB). Environment, not a regression.
- #67: coverage missing 20,928 (not bisected).
- The planner's dense coefficients (phi3's) overestimate (#4 Match: 122 GiB predicted, 80 GB peak). The F-dA-15 admission
  refused #60 by 2.1 GB, and the override then OOM'd.
- Prose/labels: gate (a)'s skip reasons still name `tp_stage.sh`, not the b1 layout.

## Runs (all `--custody-r2`)
- Bootstraps `r20260925-17*`; recording `r20260925-175229-a415` (moe67), `-175445-4e8f` (moe68), `-181422-250a` (tp70, #67),
  `-201944-cf81` (tp70b, #70), `-202204-ecb5` (big, #68, dropped), `-201729-6f0c` (tp75, #75), `-175445-08bb` (h100; supervisor killed,
  small-file copy `r20260925-234027-23b6`).
- The recording runs' own custody uploads (12–39 GB each) failed (403 on moe67, RemoteDisconnected elsewhere); their files < 20 MB
  are copied in `r20260926-021148-{30ef moe67, 4d18 moe68, 4b0e tp70, 0ccc tp70b}` (4d18 PRESERVED; the others still uploading at 02:25Z).
  Rebase runs `r20260926-004934-*` (ROWS_ROOT mode, which hits the v1 input pins) were stopped **by me** at 01:57Z and replaced by the
  CANDIDATE-mode runs below; that was the exit 143.
- Commit re-runs `r20260925-233854-*`, `r20260926-004846-55a8`; Commit outputs copied `r20260926-020557-*`.
- Rebaseline `r20260926-015749-{2654 moe67, 4cf2 moe68, 087d tp70, e70c tp70b}`; prefetch `r20260926-015601-*`, `-015735-c7fc`.
- Fixture-key mints (read-only, `--ttl 3h`, `manifests/` + `objects/sha256/`, via local): moe67 01:55Z (deleted 01:59:32Z), tp70 01:55Z
  (01:57:06Z), tp70b 01:55Z (01:56:56Z), moe68 01:57Z (01:58:07Z; the 01:55Z mint for moe68 never reached the pod).

## Spend
About $105 of $130. All pods terminated (last: tp70 and tp70b at 03:17Z), and every `vyv-rf-epoch-*` registry entry removed. The bisect cost $0.
