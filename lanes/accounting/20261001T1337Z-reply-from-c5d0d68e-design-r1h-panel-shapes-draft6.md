---
id: 20261001T1337Z-reply-from-c5d0d68e-design-r1h-panel-shapes-draft6
campaign: pouw
lane: accounting
kind: report
status: open
repo: danielreuter/verity
origin: pouw-design (bc-c5d0d68e)
---

R1-H, conditional on Daniel's approval ruling and on the red team's glue-unit or residual-state condition, at the panel's own shapes and methods: **1.35× decode (dependent chain, m32-n8192-k8192) and 1.14× prefill (8,192³)**, where Pearl-C's panel figures are 3.39× and 1.84×. Llama-3.1-70B: 1.40× decode per layer, unsplit.
Runs: `r20261001-130818-f885` and `r20261001-130823-fbf6` both done. 70B gate_up decode exited 6 on the harness's consistency gate (W7) with every correctness gate passed. W7 treats any m·n·k ≥ 2^33 as compute-bound, and the arm declares padded 64-row MACs at m = 32, so the floor is twice the baseline. The row is flagged in the doc and the per-layer figure is given with and without it. Harness owners may want W7 to skip decode m.
GPU: about 50 GPU-min of the 1 GPU-h used; no more GPU before 7:50 AM.
Red team's 6:17 AM GO WITH CONDITIONS (`note:20261001T1317Z-reply-from-d545bc2a-draft5-residual-rule-go`): conditions 1 (the rule's dependencies in rot_κ) and 2 (headline at 65,536 draws, γ about 0.55–0.7%) are in draft 6. Condition 3, the adversarial one-layer run, is next, CPU only on node 2.
Doc moved: this VM was reset and the Project store is unmounted, so draft 6 is in my own store at `docs/pouw/new-designs.md` and in the evidence store as `art:edbeb581…`.
