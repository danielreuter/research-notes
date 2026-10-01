---
id: 20261001T0528Z-finding-from-e8ffd7f2-fp4-judge-and-70b-cpu-preserved
campaign: pouw
lane: accounting
kind: finding
status: open
repo: danielreuter/verity
origin: FP4 lead (bc-e8ffd7f2, notes lane pouw-fp4)
---

# Two inherited FP4 jobs finished on node 2; both are preserved, and the 70B cross-check passes

For compute accounting and the PoUW assessor (bc-f9af3acc). No new GPU work.

- **GPU 7's cheaper-computation judge** (`fp4-gc-judge-388eeb55`, bc-dbc19788's job, exit 0 at 05:07Z):
  - It judged 141,120 tiles with #580's rule at 14d6f1bb: 3 variants (`none|pc`, `rotb8s|pc`, `rotb8s|al`) × 7 linears × 15 input families.
  - Result: 0 tiles over the cap, 0 rejected, and 0 check disagreements (588 fresh, 84 reference).
  - The adversarial families (`sparse-2of4`, the `stride-row*` families) get nothing credited, as intended.
  - Preserved as `art:86b000034451be390b6fa81b8ec50a50485db9c8a619cd5e8ae51eb0cafd1bfa`. That's the judge outputs, the summary, the words, the code and the rule tree. `out/rows` (14 GB) and `out/formed` (7.8 GB) stay on node 2.
- **Llama-3.1-70B NVFP4 CPU coverage, all 80 layers** (`f5bf-fp4-coverage-70b-cpu`, bc-f5bf55c8's job):
  - Result under the rule: 4.314% uncredited, 0 tiles rejected, worst credited tile at 0.984 of the cap (L66 `o_proj`). #556's `volunteer` gives up 0 rows.
  - Preserved as `art:678e49decaab8dd7c45057dc1e27d765cde3c31d3110058936ab8e836d8ffccf`.
- **The cross-check bc-dbc19788 asked for:**
  - Layers 0 and 79 equal the GPU gate's 8-band reference cases (`art:d146ee99…`) exactly: 14 cases, 728 counts, 924 figures, 0 mismatches, worst relative difference 0.0.
  - The other 78 layers agree in distribution with the GPU port's 16 salts (`art:c0e93d02…`): 4.25–4.32% uncredited there, 4.314% here, with the same worst linear.
- **Still running:** `fp4-kt-census-c138ca9d` (Qwen2.5-7B under the enforced rule, CPU, preemptible). I'll preserve it when it ends. #545 can close as a record after that.
