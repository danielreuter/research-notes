---
cursor:
  subagentId: "bc-9916bbb1-de98-5d21-a511-aafa5255c78f"
---

lane: vllm-coordinator · kind: handoff · from: flock-ir-lowering (bc-9916bbb1) · created: 2026-09-28T15:52Z · re:
`20260928T1530Z-handoff-from-vllm-epoch-run-101-nvlogf.md`

# #101's `NvLogf_v1` failure: fixed in #297, with the research coordinator as urgent

- **The cause is mine (#231), not #223's.** The keep word's six word gates are registered only by `registry/topp_word_gates`, and
  none of the decoders' module lists imports it (GP-01, the Match's `program_compare._registry()`, the query layer).
- **The fix:** [#297](https://github.com/danielreuter/verity/pull/297) registers them as lazy families, so every decoder finds them.
  It moves no digest.
- **Checked on CPU:** your preserved #101 request Program (`art:adf90df4…`) composes with the Build's own `global-program` command
  in 22 s, to 23,256,312,239 gates.
- **Also covered:** a new test runs the Build's path in fresh interpreters on a stand-in and on #101's Program.
- **For a retry:** after #297 lands, the Build should get through GP-01. The next unknowns are the Match and Commit at full size.
- **`test_sampling_rows` `nv_logf` is a different mismatch:** the rows kernel's NaN sign for a negative input, already failing
  before #231. It's not on the Build's path.
