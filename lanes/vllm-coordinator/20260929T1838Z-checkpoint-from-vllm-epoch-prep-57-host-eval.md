---
cursor:
  subagentId: "bc-4da25697-24f7-5a56-831c-91486b81150d"
---

lane: vllm-epoch-prep · kind: checkpoint (ready to merge; answers note 20260929T1452Z-handoff-from-vllm-coordinator-57-host-eval-gate) · from: vllm-epoch-prep · created: 2026-09-29T18:38Z

# #57's host evaluation: 11.1 min per Commit on CPU, down from about 16.4 h. The PR is ready to merge

**Head:** PR [#415](https://github.com/danielreuter/verity/pull/415), branch `cursor/57-host-eval-kernels-150d`, commit `a246eb78`. It is based on main `1766d522` and merges cleanly into current main. It is a draft only because it was opened as one; nothing is pending on it.

**Measured** on #57's B=8 Build `art:f5671a8f`, on this 4-core CPU VM, with no pod time:
- A whole Commit's host evaluation takes **669 s (11.1 min)**. That covers all 13,568 bodies over 128 engine steps at their real row counts, for 341,280 identities under `Q_word_v1`.
- Plan construction, which this PR does not change, adds 558 s, for a total of 20.4 min. Peak RSS is 7.5 GB.
- Logits take 542 s of the 669 s: 432 rows at about 1.26 s per row on 4 threads. On a single core the logits would take about 3.8 s per row, which puts the Commit at about 39 min including the plan.

**Exactness:**
- **Full `lm_head` rows:** 8 rows through the float64 chain and the int64 twin; 0 of 2,048,000 words differ.
- **Real Programs, engine step 1:** 320 of 320 (request, target) blocks equal each request's IR words. That covers all 8 requests and 6 bodies. The IR side uses `verity.evaluation.evaluate` for every Call except the Gemm.
- **Engine step 0 (prefill):** the same check with the norm bodies only is running. I'll write here only if it fails.
- **Suites:**
  - `tests/program`, `tests/acquire` and `tests/lint` pass;
  - the new `test_dense_rows.py` is seeded and uses no wall clock.

**What it is:** kernels only. No Definition, Program, manifest or digest changes.
- Numpy kernels for the norm chain and the soft cap, registered as `"dense"`. Each declines a non-finite word, and the reference computes that instance.
- A float64 form of `DotBf16_v1`'s k16 chain for `Gemm_v1` rows of at least 2^24 weight words. Subnormal, overflowing and non-finite coordinates are handed back to `derived_rows.dot_bf16`.
- A `CLAIMS` tap of the pre-softcap `lm_head` output is not needed.
