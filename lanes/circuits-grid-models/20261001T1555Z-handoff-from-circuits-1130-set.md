---
id: 20261001T1555Z-handoff-from-circuits-1130-set
campaign: verity
lane: circuits-grid-models
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits (@circuits, bc-b8aaadaa)
---

# @circuits (8:55 AM PDT): pk2 answers, and the 11:30 AM PT goals the grid carries

**Your three items:**
- **Done:** lifted the qwen3-06b packing stop (`dispatch.py pack-lift`, citing the SiluMul_v1 edge).
- **Yes to `-pk3` twins** for gm005 (r1-distill-qwen-15b) and gm008 (qwen25-3b). Submit them on node 1 so they route through `route()` and pack.
- **The `n2_build.sh --task 1` bypass:** I'm passing it to infra.

**The 11:30 AM PT goals (Daniel's set, numbers are floors):**
1. **Grid ≥ 450 ended deployments, ≥ 30 models, 11 families, every failure with a named cause.** Register 2–3 more small ungated models now
   (staged checkpoints, TP1), smallest first, to pass 30 models with the epoch run's. A separate worker audits the epoch run's 83 failed attempts.
2. **Node-1 held-but-idle ≤ 40% for circuits' Commits, 9:30–11:30** (circuits owns it now; infra measures hourly). From 9:30:
   - favor packable rows (≤ 4B, TP1, b ≤ 8, on the boundary tree), so the pack pods stay full;
   - among the rest, favor rows with real GPU work (B8 / 1k-token);
   - keep Gemma-2 held.

   circuits-replay-keep-leaves is making non-packed Commits take their GPU by lease only after pod startup (infra's circuits lease pool, pilot
   ~9:30). When it tells you how, mark new non-packed items `lease: self`.
3. Report counts at 10:30 and 11:20 AM PDT in lanes/circuits/: ended on both nodes, models, families, failures by cause.
