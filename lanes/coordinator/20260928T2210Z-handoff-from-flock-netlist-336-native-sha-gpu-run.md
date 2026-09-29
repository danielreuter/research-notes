---
cursor:
  subagentId: "bc-ff572e70-b0e7-5094-85be-13ff9ddc4d6a"
lane: coordinator
kind: handoff
from: flock-netlist / M0 (bc-ff572e70)
to: the backend sweep lane (bc-ea1c2c4f), via verity-root
created: 2026-09-28T22:10Z
---

# #336, the native SHA-512 witness kernel: one L40S run for byte identity and timing, within the hour's remaining ~$0.65

**HELD (2026-09-29 08:35Z, verity-root):** the overnight budget window is over, so this run waits for Daniel's budget. Please don't run it until then.

- **The PR:** [#336](https://github.com/danielreuter/verity/pull/336), head `2e5745a0eb611928795b86403a16c0722cb14f76`. It's #327 plus #328 plus the kernel.
- **The bundle:** `artifacts/native-sha-2e5745a0-on-adcf38bf.bundle`, which is `adcf38bf..2e5745a0`.
  - sha256 `04eabc2973239c05d6f5e7818e5d354a9a2d319b213d73a5e8514976ca56a1c7`, 2,736,609 bytes.
  - `git bundle verify` says okay, and a clone holding only `adcf38bf`'s history fetches it to `2e5745a0`.
  - Please merge #212 on top for its statement-cap options, as for #327.
- **Run 1, byte identity:** B = 16, `SELFTEST=1 SELFTEST_GPU=1 SELFTEST_CASES=gpu_paths_agree,gpu_proofs_match_cpu`, on the two GEMM coordinates.
  - `gpu_paths_agree` now runs the level-by-level compression pass on one side and the native kernel on the other, so its `native_sha` should read `[true, true]`.
  - Pass: `proofs_equal` and `transcripts_equal` in both cases.
- **Run 2, timing:** m = 34, `BATCH_ANDS=2^32 MAX_STATEMENT_BITS=2^34 WARM=1 RUNS=3`, as in `r20260928-213503-2861`.
  - Please report `t.witness_comp` and `t.witness` per rep, and the median prove, against #327's run (`t.witness` 0.27–0.35 s per rep there).
  - The plan expects `t.witness_comp` to fall to a few tens of milliseconds.
- **If run 1 fails,** please skip run 2 and send me its per-case lines (`selftest.gpu_cases`). `FC_NATIVE_SHA=0` turns the kernel off without a rebuild.
