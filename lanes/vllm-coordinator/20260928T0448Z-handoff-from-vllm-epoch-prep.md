---
cursor:
  subagentId: "bc-4da25697-24f7-5a56-831c-91486b81150d"
---

lane: vllm-epoch-prep · kind: handoff · from: vllm-epoch-prep (bc-4da25697) · created: 2026-09-28T04:48Z

# S1 finding: #57 and #74 have Call-level boundaries serving doesn't commit; under Q_word as record their Commits fail unless those values get a source

**What I measured (CPU, stored Builds, the smallest request shape of each).** Today's population (`Q_module_body_v1` + policy)
against the Call-level boundaries Q_word needs: `word.check_query` non-strict, plus the Values a Call-granular population adds.
Script and output: notes `lanes/vllm-epoch-prep/evidence/s1_call_boundaries.py`, `/tmp/ab/s1_cb_small*.json` (to be preserved).

| Row, Build, shape | Calls | Required today | Call boundaries | Extra Values | Where |
|---|---:|---:|---:|---:|---|
| #57 unset `art:f5671a8f` LP31_T52 | 92,897 | 30,884 | 92,996 | **62,330** | Gemma's ATen norm chain (`SquareF32`, `MeanTriton`, `AddScalarF32`, `RsqrtF32`, `ScaleRow*`, `MulVecF32`, `NarrowF32ToBf16`), every norm |
| #57 `once` `art:3ede2457` LP31_T52 | 87,437 | 30,884 | 87,536 | **56,870** | same chain (the `+ 1` repeats gone) |
| #74 unset `art:fcd189dc` LP73_T1 | 144,008 | 139,404 | 160,281 | **21,312** | `Fp8GroupQuant_v1` outputs (x_q, x_s) read by `ScaledMmFp8Block` inside `qkv/o/gate_up/down_proj`; plus the shared-scale recompute S4 removes |
| #73 unset / check-inf `art:24c603a7` / `art:622fbaf1` LP10_T8 | 32,454 | 34,186 | 34,014 | **0** | none |

#101 was already known clean (fine-query-plan §0). The other rows' record `result.json` files aren't in the stored programs
artifacts, so I can't run the check on them from the VM; their structure (fused norms, one Call per module) matches #73/#101.

**Why it matters.** Q_word commits every Value one Call produces and another reads. Serving captures module outputs, so these
interior Values have no source. With S1 as written, #57 and #74 (GREEN) would fail at Commit on the GPU.

**Options (your call; I'm continuing S1 so it's ready either way):**
1. **Host-evaluated sources** for Call-level boundaries whose producers read only committed Values (the chain from the norm's
   committed input and weights; the quant from the linear's committed bf16 input). This is the `scale_products` pattern, generalised
   and exact by the IR's own evaluation. Soundness is unchanged: the consuming unit still checks against the GPU-captured output. It is new
   committer code (one source, two rows), CPU-testable, but not done by 08:00Z alongside S1-S4.
2. **Restate Gemma's norm as one Definition** (the chain folded into one Call; only its scale, the existing Gemma norm-scale policy,
   stays committed). #74 still needs option 1 for x_q / x_s: every output coordinate reads the whole row, so they are committed words
   either way. S4-B's `scale_products` source needs x_s too, and x_s isn't committed today.
3. **Record #57 and #74 under S1 anyway** and accept FAIL verdicts (#57 is FAIL class already; #74 would move GREEN to FAIL), or defer
   those two rows' GPU runs until option 1 lands.

My recommendation is option 1, as a follow-up PR after S1. Meanwhile, defer #74's GPU run (and #57's, unless its current FAIL class is acceptable).
