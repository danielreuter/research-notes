---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: coordinator · kind: handoff · from: vllm-coordinator (bc-ecac3029) · created: 2026-09-27T03:10Z

# Verdicts on #103, #98, #99 and #102, measured against main 3040ac1f (after #96)

| PR | Head | Verdict | Why |
|---|---|---|---|
| **#103** top-p `splits` total | `cbe3db97` | **APPROVE, merge request** | The test fix is in; see below |
| #98 cross-Call check + `unit_rule` member check | `d7f76916` | HOLD: re-merge main | Conflicts with main in `pipeline/manifest.py` (#96's `taps` against #98's `cross_call`, both added to the same signatures and CLI) |
| #99 tap labels + graphs | `13c294d6` | HOLD: one lint | `test_no_by_name_rules::test_every_by_name_rule_is_allowlisted` fails: the new `_STREAM_NEW` table (`word.py:487`) and `head in _STREAM_NEW` (`word.py:509`) are by-name rules missing from `by_name_allowlist.json` |
| #102 MS class | `40ec2e13` | HOLD: re-merge main | Conflicts with main in the README, `config.py` and `pipeline/manifest.py` (#96). The evidence is complete; see below |

## #103 @ cbe3db97: APPROVE

- Merges cleanly into main 3040ac1f, and with #99.
- My jdiff of main against main + #99 + #103 (over `tests/program`, `tests/query`, `tests/pipeline`, the lints and flock's
  `test_ir_sampling`):
  - #103's tests pass, including the updated `test_sampling_rows` assertion (line 325 now asserts an all −inf row);
  - the old refusal cases are replaced by the keeps-no-lane cases;
  - no new failure comes from #103.
  - Of the two new failures in that run, one is #99's by-name lint. The other, `test_twins::test_check_writes_the_evidence_schema`
    (`openmp`), depends on the environment: it passes in isolation on both trees.
- No digest moves: `TopPMaskWordx128256_v1` is `b7202a75…` on both trees, and row #101's Program and manifest stay as recorded.

## #102 @ 40ec2e13: the evidence is complete; approve after the re-merge

- **Kernel changes compile away when the flag is off:** the `MS` class and store are behind `VERITY_MAT_SRC & 64`. The guarded
  builds are 123, the default builds 59. `StreamLayout(ms=False)` keeps every offset, the total and the digest.
- **Exactness:**
  - FA2 on L40S `r20260927-012901-955c`: 547,438 MS words equal the IR, softcap included.
  - FA3 on H100 `r20260927-012825-34ba`: `ok: false` only from the 40 −inf-max words (the FA3 `Check_inf` IR finding, which I
    accepted at 02:00Z).
  - out and lse are bit-identical in every case.
- **#101:**
  - flag off: run root = record, manifest `90f81868…`, the same as base main from the same Build;
  - flag on: 242,688 `max_scaled` words, equal to the checker's count and the tap list's.
- **Checker:** 0 violations and 0 recomputes.
- **Gate (b)** (base 84801045): jdiff rc 0, 0 new failures, 9 new tests.
- **After the re-merge:** I'll re-diff the touched directories against main and send the merge request.

## Item 2: routing the two real recomputes

No lane owns the vLLM FP8 Definitions or Gemma's Build path, and cross-call-check is carrying #98 and #99, so I wrote a lane brief:
`internal/lane-briefs/vllm-recompute.md`. It is **ready to launch** as `vllm-rf-recompute`.
- **Both fixes land opt-in, behind construction selectors,** with digests of record fixed and a with-selector-off A/B:
  - #74's FP8 block scale product: computed once and committed;
  - #57's Gemma norm weight + 1: issued once per norm in the Build.
- Switching the record is a re-baseline epoch item.
- It's CPU first, and any H100 or L40S check goes to root with an estimate first.

## Item 3: pod Builds for #4 and #101

**Recommend yes, together with Daniel's serving-view request:** one L40S, Build stage only, both rows. About 2.5 h, about $2.7,
cap $4. The details are in `internal/lanes/coordinator/20260927T0300Z-scope-vllm-shaped-serving-program-101.md`.
- The run must reproduce #101's recorded Program `ccc21347…` (and #4's). If it doesn't, the lane stops.
- **Owner:** vllm-cross-call-check, after #98's re-merge.
- **Waiting for root's approval** before any pod.
