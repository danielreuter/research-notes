---
id: 20260929T1750Z-handoff-from-pous-389-line-extension
campaign: verity
lane: verity-root
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# POUS -> root: #389 end-to-end run needs its line extended to 22:00Z and raised to $2.85

Daniel's priority is a working end-to-end PoUW run, so I'm asking for more room on the #389 line.

- **What happened:** no pod could run the pair before a verdict, so there are no honest or tamper run ids.
  - COMMUNITY 4090 stock was empty from 17:16 to 17:37Z.
  - The first SECURE 4090 (EPYC 7702) failed the CPU gate at 68.9 s per forward, against the 40 s limit. Run
    `r20260929-173822-d2e7`, labelled.
  - The cost was $0.04, so the line stands at $1.63 of $2.55. No pod is running.
- **Cause and fix:** the committer caps threads at `min(16, …)`, so a 256-thread 7702 uses 16. bc-dd22acf8 raises
  the cap (bit-identical results) and measures the gate on one 7702 pod, about $0.03, inside the current line.
- **Request, for the line `vy-pouw-mvp-qwen05` in `budgets.toml`:**
  - extend the expiry from 19:00Z to 22:00Z;
  - raise the cap from $2.55 to $2.85 (+$0.30). The pair needs about $0.95 and 1.4 pod-hours at $0.74/h, and about
    $0.89 remains after the gate.
- **Launch rule:** the pair launches only if the gate passes 40 s and your extension is on research-notes. Otherwise
  the worker stops and reports.
