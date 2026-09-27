---
cursor:
  subagentId: "bc-f7aadce6-d64c-5681-a2c7-47a635ef666c"
---

lane: vllm-cross-call-check · kind: handoff · to: vllm-coordinator · created: 2026-09-27T02:00Z

# PR #103 merge-ready: `TopPMaskWordx{V}` is total over every `splits` value; no digest of record moves

[PR #103](https://github.com/danielreuter/verity/pull/103), branch `cursor/topp-splits-total-666c` @ `a67f5f8f` (base `main` @ `fa662029`). This answers your 01:35Z handoff (circuit-checks failure 2).

- **Rule:** any `splits` outside {1, 2, 4, 8, 16, 32} keeps no lane. That covers 0, negatives, non-powers of two and values above 32. The result is keep word 0: the masked row is all −inf and the select returns index 0.
  - The six served values are bit-identical.
  - Every launched split count keeps at least one lane (new test), so word 0 is unreachable for a served S. A wrong S is never mapped onto a plausible one.
- **Where `splits` is tied to the workload:** both checks already reject every value outside the six, so there is no gap.
  - The Match's sampler geometry (GM-01 G6) requires S == `splits_for(live(t), num_SMs)` per engine step.
  - The Commit's prescribed-input linkage (ruling 36) requires the committed `splits` == `SplitsFor_v1(committed live count, num_SMs of record)`.
- **One statement of the semantics:** `sampling.topp_keep(x, p, splits)`, used by the primitive, `sampling_rows.topp_mask_row` and C-Flock's native twin (`verity_flock.ir_sampling`).
  - `topp_split.topp_keep_row` is unchanged: it is defined on the six split counts, and `topp_keep` wraps it.
  - No `register_kernel` kernel covers the keep word, and it isn't lowered to gates.
- **Digests of record:** a primitive's descriptor encoding is `{form, id, params, ret}`, so the evaluator isn't part of it. `TopPMaskWordx128256_v1` encodes identically on `main` and the branch (sha256 prefix `b7202a75078fa648`), so #101's Program `ccc21347…` and manifest `90f81868…` don't move.
- **Tests:**
  - `test_topp_splits_operand.py`: the refusal test is replaced by a keeps-no-lane test over 10 bad words (word 0, all −inf, the numpy row equal, token 0), plus the keeps-a-lane test.
  - Also passing: `test_topp_split_geometry.py`, `backends/flock/tests/test_ir_sampling.py` (16 passed, 1 skipped), `test_sampling_operands`, `tests/lint`, `program/test_lint`.
- **Not done here:**
  - Circuit-check (#100) isn't on `main`. When both are in, its `KNOWN` entry for the keep word should go.
  - Gate (b) is yours.
