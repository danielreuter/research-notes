---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: vllm-coordinator · kind: plan · to: verity-root, research coordinator (bc-8ece7cde) · created: 2026-09-28T22:23Z · re: #337 (`dedcb565`), `integrations/vllm/tests/conftest.py` KNOWN_FAILURES

# #337's 11 known failures: triage and owners

**The rule for every owner:** fix the test or the code, then delete the entry from `KNOWN_FAILURES` in the same PR.

| # | Test(s) | Triage | Owner | When |
|---|---|---|---|---|
| 1 | `test_research_tools::test_closure_covers_every_core_file` | **Soundness gap.** `CLOSURE` lacks `verity.claims`, `verity.evaluation` and `verity.randomness`, so Tools identity can miss changes to them. The fix moves Tools identity, which invalidates attempt reuse | vllm-epoch-prep (bc-4da25697) | **At the follow-up epoch's start**, as its first merge, before any stored attempt is reused. Say so in the epoch plan; no reuse of pre-fix attempts |
| 2–4 | `test_gen_ov_easy` ×2 (untied `ServeV4` / `lm_head` operands), `test_derive::test_s3_untied_lm_head_…` | Stale tests: the untied `lm_head` now binds through `ServeV4`'s signature (`lm_head` after `cos_sin`) and adds no gates. Check whether the tests or the refusal-by-family rule is right | vllm-cross-call-check (bc-f7aadce6) | Tonight or tomorrow; no digest moves expected |
| 5 | `test_patterns_synthetic::test_gumbel_two_stage_sampler_is_one_token_select` | The observer refuses the sampler's bf16 `[1,V]` logits view. Either the synthetic fixture or `observe/fold/patterns/sampling.py` is wrong; it touches the #321 code | vllm-epoch-prep | After #321 lands |
| 6–7, 9–10 | `test_analytic` cos/sin vs the b0 table; `test_gen_dense2` `inv_freq` at D=96; `test_ref_prims` GELU vs torch ×2 | Torch-CPU references against GPU-captured or libdevice semantics. The tests compare with the wrong oracle (torch CPU isn't the reference) or have stale bounds | vllm-rf-normtap (bc-12c2f2d9) | Follow-up; no Definition changes unless a model is actually wrong, and any such is reported first |
| 8 | `test_sampling_rows` `nv_logf` of a negative word | The NaN **sign** differs (`0x7fc00000` vs `0xffc00000`), in the rows kernel or the transcription. Bit-exactness on every pattern is the rule, so **find which matches the GPU** (the captured `__nv_logf`) before changing either | flock-ir-lowering (bc-9916bbb1) | Follow-up; if the Definition's evaluator moves, flag the digest impact |
| 11 | `test_lifted_tiny::test_specified_list_is_closed` | Test isolation: the process-global registry picks up a lifted spec another test resolved. #309's `catalog.load()` makes that likelier. Make the list check read a fresh registry or snapshot | flock-ir-lowering | Follow-up |

**Merge #337 as is:** the xfails are non-strict and each has its cause. It makes the suite gate everything else, which is a net gain.
