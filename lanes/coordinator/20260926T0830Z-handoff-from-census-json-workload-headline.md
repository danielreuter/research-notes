---
id: 20260926T0830Z-handoff-from-census-json-workload-headline
campaign: overnight-sep25
lane: census-json
kind: handoff
status: open
repo: danielreuter/verity
origin: cursor/workload-headline-574a
---

# census-json: the per-workload headline (goal 3) is ready. Merge request (PR #61)

**To:** research coordinator (bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628).

## Merge request

- **PR:** [PR #61](https://github.com/danielreuter/verity/pull/61), `cursor/workload-headline-574a` into `main`. It is one commit on top of main `e3a2d81d`, and it merges cleanly.
- **Tests:** the whole `backends/numerical` suite passes (914). The new tests are in `tests/bench/test_headline.py`. CPU only.
- **Parity:** the existing tables are byte-identical to main in the legacy markdown and JSON, the raw views JSON for every rule set, the frozen tables and parity. The spec markdown only gains the new section.

## What it computes

For each census workload and each backend, it computes the share of the served run's native work covered by published, cleared cells, and the work-weighted overhead over that share. It is the markdown section "Workload headline" after Table 3, and the entities key `workload_headline`. Under the legacy rules it is omitted in the markdown and `null` in the entities.

- **Units:** VUs × subcircuits per VU, per bound subcircuit, from the census `template_mix`.
- **Native work:** the census work model on the **served** hardware line, in two bases (sp1-evaluator's):
  - **Tensor-peak GEMM:** GEMM-like templates at the dense tensor peak; the others memory-bound.
  - **All memory-bound:** a GEMM coordinate reads its weight row.
- **Covered:** an admissible result of that backend on exactly the same subcircuit (template and bound parameters, semantics included), cleared (not provisional, no open finding), with its prover on the served hardware.
- **Overhead:** Σ units ÷ P over Σ native seconds of the covered subcircuits, taking the highest-P result per subcircuit.
- **Uncovered:** listed with a reason and never imputed. The reasons are `no census subcircuit`, `no result`, `only on <hardware>` and `not cleared`. Templates with no work model are listed and left out of both sums.
- **Intervals:** attention's T is known only to its block (NB, last). So native work, shares and overheads are intervals.

## #101 today

Every backend covers 0% of #101's work.
- **Mismatch:** #101 was served on an L40S (`sm80.mma` bf16, FA2 semantics). C-Flock's cleared elementwise cells ran on the H100, so they show as "only on H100 SXM5".
- **No census subcircuit:** attention, embedding and sampling have none yet.
- **Native time:** 5.98–11.4 ms on the tensor-peak basis, where attention is 64–81%; 0.67–0.68 s on the all-memory-bound basis, where GEMM is about 99%.

## Decisions to surface

1. **Strict hardware matching:** this follows the task as written, "a cell on matching hardware and semantics". A cell on another GPU does not cover a subcircuit. For #101 that means the figure stays at 0% until cells are proved on an L40S at `sm80` semantics, or a headline is taken over an H100-served workload.
   - **Alternative:** count cross-hardware cells, with N still on the served line. sp1-evaluator's cover did this, with a 4090 prover against L40S native.
   - That is a semantics change, so I have not made it. It would be one predicate in `headline.headline`.
2. **Census byte models I added:** `attention-head` and `gumbel-top-p-token-select` are from bench-spine's ports. `token-select-greedy`, `embedding-row`, `bias-add`, `bf16-mul-scalar`, `moe-sum`, the MoE expert coordinates and `scaled-mm-fp8-block-coordinate` are from the Definitions' operands.
   - `moe-router-topk` has none yet, so it shows as not modelled in both bases for the two OLMoE workloads.
   - Adding a byte model for it needs the router logits' dtype.
3. **L40S bandwidth:** 864 GB/s, from the datasheet, on both L40S lines.

## Next

When attention, sampling and embedding get bound census subcircuits with ids, and cells land on the served hardware, the headline fills in with no code change.
