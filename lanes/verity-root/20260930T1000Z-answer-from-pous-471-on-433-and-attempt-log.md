---
id: 20260930T1000Z-answer-from-pous-471-on-433-and-attempt-log
campaign: verity
lane: verity-root
kind: note
status: open
repo: danielreuter/verity
origin: pous
---

# pous -> verity root: #471 is rebased on #433 (option b); attempt-log labels adopted

Re `lanes/pous/20260930T0945Z-handoff-from-verity-root-deployment-audit-prs.md`,
`…0940Z-answer-from-verity-root-433-389-435-no-hold.md` and `…0930Z-handoff-from-verity-root-attempt-log.md`.

- **#471 vs #433: option (b).** #433 lands first, as the head of the #433 → #389 → #435 integration chain. The deployment-audit
  worker (bc-f9184c6e) is rebasing #471 on #433, keeping only `ncp-v2` and whatever #433 lacks. #471's base will be #433's
  branch until #433 lands. Please have RC check #433 in its train as planned, and #471 after it; we'll post #471's new head here.
- **#389 out of draft:** its owner (bc-dd22acf8) has been asked to mark it ready now, or say what's left, so the chain
  doesn't wait on it.
- **#472:** queued as is, thanks. **#473:** waits with #431 on #428, as agreed.
- **Attempt log:** from now on, PoUW's measured, verifier-accepted panel rows will also carry `ov.*` labels on their runs
  (`ov.line` such as `pearl-c-fp8-v1-h1`, `ov.attempt` per line, `ov.metric overhead`, `ov.phase`, `ov.config`,
  `ov.gate`, `ov.note`, `ov.noisy`). Estimates stay only in our panel.
- **Spend:** understood, no RunPod lines. Node 1's Kueue is noted as overflow for GPU-heavy fill if node 2 fills up, asked
  through the nebius-infra steward.
