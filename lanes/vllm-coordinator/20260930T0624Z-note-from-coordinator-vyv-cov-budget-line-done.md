---
cursor:
  subagentId: "bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628"
id: 20260930T0624Z-note-from-coordinator-vyv-cov-budget-line-done
campaign: verity
lane: vllm-coordinator
kind: report
status: done
repo: danielreuter/verity
origin: coordinator
---

# DONE: the `vyv-cov-` budget line is live in the budgets guard (06:22Z)

Answers `lanes/coordinator/20260930T0521Z-ACTION-from-vllm-coordinator-budget-line-coverage` (root approved 06:20Z, within the overnight ceiling).

- **Line**, exactly as requested: `"vyv-cov-" = { cap_usd = 150, expires = "2026-10-01T14:00Z", max_pod_hours = 12, … }`.
- **Guard scope:** `vyv-cov-` is added to `[guard] project` (now `vy-`, `vyv-rf-epoch-`, `vyv-cov-`). Without it the guard would not watch these pods at all.
- **Live:** research-notes `origin/main` at `16be7926`. Parsed by both `tomllib` and `research.pods.budgets.load`. `research pods guard status` read it at 06:22:12Z and shows `'vyv-cov-': $0.00 of $150, expires 2026-10-01T14:00Z, max_pod_hours 12`.
- **Watch:** the RunPod balance was **$127.92** at 06:22Z, below this line's $150, with the guard's floor at $25. So the balance, not the line, is the binding limit tonight: about $100 of new spend across every line before the floor. Your $25 tripwire still applies.
