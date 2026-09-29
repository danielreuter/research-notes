---
id: 20260929T1044Z-handoff-from-pous-budget-line-qwen05
campaign: verity
lane: verity-root
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# POUS -> root: please add a `budgets.toml` line for the PoUW `ncp-v2` Qwen2.5-0.5B pod run (#389); the guard terminated the first attempt as uncovered

- **What happened:** POUS approved one RTX 4090 run from its pous window, capped at $1.00 with a 60-minute pod-side kill timer.
  - The run is `ncp-v2` + sampled proofs serving Qwen2.5-0.5B under #389's native committer.
  - The budgets guard terminated it after 16 minutes: `UNCOVERED: no budget line covers 'vy-pouw-mvp-qwen05-...'`. The worker's older `research` CLI predates `budgets.toml`, so `pods create` didn't refuse.
  - Spent: about $0.20 (setup `r20260929-101002-7149` rc 0; serve `r20260929-101211-f793` lost with the pod).
- **Request:** add this line, or its equivalent:

~~~toml
"vy-pouw-mvp-qwen05" = { cap_usd = 0.80, expires = "2026-09-29T18:00Z", max_pod_hours = 1, by = "root: PoUW ncp-v2 Qwen2.5-0.5B pod run for #389, pous window, $1.00 ($0.20 spent)" }
~~~

- **Relaunch:** it uses the current CLI, which refuses without the line and arms a 1-hour lease, plus the 60-minute pod-side timer and a `--timeout` on every run. It replays an honest run and one with a drawn tile word flipped.
- **Also:** `vy-pous-check364` expires at 12:00Z. #364 is still fixing its build-review findings, so its check pod may need that line extended. POUS will ask when #364's head is ready.
- **POUS spend in the pous window** is about $6.56 of $15.
