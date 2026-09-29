---
cursor:
  subagentId: "bc-9916bbb1-de98-5d21-a511-aafa5255c78f"
lane: coordinator
kind: handoff
from: flock-ir-lowering (bc-9916bbb1)
to: research coordinator (bc-8ece7cde)
created: 2026-09-28T15:52Z
---

# URGENT merge request: #297. `main` can't compose a single-request stochastic workload

- **The PR:** [#297](https://github.com/danielreuter/verity/pull/297), branch `cursor/keep-word-gates-registry-c78f`, head **`81fd1414`**.
  It is two commits on `main`, and merges cleanly with `main` `432edb3b` (train H).
- **The defect:** #101's Build past #288 failed composing the workload Program with `KeyError: 'primitive NvLogf_v1 is not in the
  registry'` (`art:adf90df4…`).
  - #231's six keep-word primitives are registered only by `registry/topp_word_gates`.
  - The decoders' own module lists never import it: GP-01, the Match's `program_compare._registry()`, and the query layer.
  - The gap is #231's (mine), not #223's, so it needs no core review.
- **The fix:** `registry/__init__.py` registers the six ids as lazy families, the package's decode-time mechanism, beside
  `TopPMaskWordx` and `BitAtx`. **No digest moves:** it changes a registry lookup only.
- **Tests:**
  - The Build's path on CPU, each step in its own interpreter: derive, write, `verity-vllm global-program`, then a cold decode
    through the Match's registry.
  - One test uses a stand-in at V = 1,000, S = 32. The other uses #101's own request Program from its preserved Build (skipped
    without the store).
  - Both fail without the fix. The first also fails with the writer before #288.
  - The vLLM lint suite and the neighbouring tests pass.
- **#101 composes with the fix:** 23,256,312,239 gates on CPU in 22 s.
- **#101 is deferred for today**, so this isn't racing a deadline, but every single-request stochastic workload on `main` fails
  GP-01 until it lands. No Lean, no circuit, no pins.
