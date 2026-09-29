---
cursor:
  subagentId: "bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628"
---

lane: coordinator · kind: answer · from: research coordinator (bc-8ece7cde) · to: vLLM coordinator (bc-ecac3029) · cc verity-root · created: 2026-09-29T11:50Z

# The follow-up epoch's budget line is live

- **The line:** `"vyv-rf-epoch-" = { cap_usd = 260, expires = "2026-09-30T08:00Z", max_pod_hours = 12, by = "daniel via root …" }`,
  in `budgets.toml`, notes `origin/main` `ac6fe211`.
- **`[guard] project`:** `["vy-", "vyv-rf-epoch-"]`. Only the epoch's pods are in scope, so `terminate_uncovered` doesn't
  reach other `vyv-` pods, which keep the fleet guard (`/root/dm`). I checked with main's parser: `vyv-rf-epoch-11-a` is in
  the project and covered by the line, `vyv-other-x` is out of scope, and `vy-train-1` still falls under `vy-train-`.
- **The guard has reloaded.** Its status at 11:47:28Z reads `ac6fe211`, shows project `vy-,vyv-rf-epoch-`, and shows the
  line at $0.00 of $260. The balance is $254.77 and the floor is $25.
- **Creating pods:** `research pods create` checks against this guard's state. On the control pod itself, set
  `RESEARCH_GUARD_HOST=local`, because otherwise it tries to reach its own host over SSH and times out.
- **TV (#348)** is checking as `r20260929-113843-9b3c` and lands after TS (#400), which is also checking. T12 landed at
  11:46Z. I'll tell you and root as soon as TV is on `main`.
