---
id: 20261001T0719Z-handoff-from-circuits-decisions
campaign: verity
lane: circuits-grid-models
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits (@circuits, bc-b8aaadaa)
---

# @circuits: decisions on your 0707Z handoff. Hold for go; 360 rows plus 12 TP1 rows for the 14B models; 11 families

1. **Hold, the default.** Submit nothing until circuits sends go. Daniel's order is that every Commit be re-verifiable on Boolean later, so
   the grid tree must carry circuits-replay-keep-leaves' change first (expected about 1:30 AM PDT; circuits sends go once it does).
   Meanwhile, finish the checkpoints.json entries, the tests, and the push and sync. Have the first wave ready to submit within 10 min of
   go: TP1 B1/B8 of the 10 models under 7B first, then the rest.
2. **B16+ of 7B+ and MoE:** keep release.py's hold. The plan stands at 360 rows.
3. **The 14B models:** yes, add TP1 B1/B8 rows for qwen3-14b and phi4-14b on node 1 (12 rows; both fit one GPU at 29 GB). Their TP2 rows wait
   for infra's answer on routing TP2 to node 2, which circuits asked for.
4. **Families:** accepted, one id per publisher model series, with base, instruct and coder variants together and the R1 distills under
   their base. Don't count pythia (unsupported) and don't split out the MoE or distill families, so 11. Report the count that way.
- Keys `cov-gm01`…, with env and resources like cov-cg10 and a research question on every item: fine.
