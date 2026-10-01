---
id: 20261001T0202Z-handoff-from-circuits-rebase-565-566-582
campaign: verity
lane: vllm-staging-bug
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits (@circuits, bc-b8aaadaa)
---

# @circuits: after the MKL warm-up, rebase the sm_120 FP8/FP4 linears #565 → #566 → #582 onto proofs' consolidated FP PR

tc-gemm (their author) has been silent since 5:31 AM PDT, so this comes to you.
- **Base:** proofs' consolidated step PR, branch `cursor/proofs-fp-defs-95d4`, carries #487, #515, #502 and #523 (E4M3, E5M2, MXFP4, NVFP4 steps,
  `GemmCoordinate` Definitions, C-Flock pieces). Those four close when it lands. Until proofs posts the PR link (Slack thread
  1790818944.596569), rebase onto that branch's tip.
- **#565** (the per-tensor FP8 linear; supersedes #516): the hygiene audit reports a conflict in `targets.py`. Rebase it with a merge commit, no
  force-push, keeping both sides' target rows. Then **#566** (the NVFP4 linear, on #565) and **#582** (block FP8 over CUTLASS, on #566).
- **Checks:** each PR's tests, `circuit-check` for each new Definition, and the cc 12.0 binding tests. Don't change step Definitions; they're proofs'.
- Post each new head in `lanes/circuits/`. I'll get them granted. #516, #524, #535 and #539 stay open until the top-level relays Daniel's
  ruling on superseded PRs.
