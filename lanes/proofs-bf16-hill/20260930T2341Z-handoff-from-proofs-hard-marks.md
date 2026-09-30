---
id: 20260930T2341Z-handoff-from-proofs-hard-marks
campaign: verity
lane: proofs-bf16-hill
kind: handoff
status: open
repo: danielreuter/verity
origin: proofs (bc-8416bc72, Slack @proofs)
---

# Urgent, 4:41 PM PDT, Daniel's reset: first BF16 point on the console by 5:40 PM PDT; all four K by 7:40 PM; the overhead-vs-K curve by 11:40 PM

These are the goals of record (Project store `docs/goals.md`). Only these marks count.
- **By 5:40 PM PDT: one BF16 point on the console.** Take the fastest path: run M0's existing bench (the #20 tree,
  `gemm_slowdown.py` `per_coordinate`) at **K=2,048** as step 0 through `research run` on node 1 (`provers`, 1 GPU; the GPUs
  are idle).
  - Compute overhead with the census peak. If the entry isn't sourced yet, use the datasheet figure you've found and flag it.
  - Append the point to `/workspace/usage/hillclimb/bf16-GemmCoordinate_v2-K2048.json` on vy-nebius-1 (write whole, then
    `mv`).
  - If the full bench takes more than ~40 min, run a single statement's timing (median of 3) instead.
- **By 7:40 PM PDT: baselines at all four K** (2,048, 4,096, 8,192, 16,384) on the console. Run them **in parallel** on
  separate GPUs, one job each.
- **By 11:40 PM PDT: overhead against K** for BF16 on the console, plus hillclimb steps if time allows.
- **Verifier overlap moves to a new worker** (lane `proofs-verify-overlap`, branch `cursor/proofs-verify-overlap-95d4`).
  Don't do that lever; it appends its own point to your K=2,048 roll-up as a labelled step.
- Push your branch after each step, and checkpoint at each mark with the numbers.
