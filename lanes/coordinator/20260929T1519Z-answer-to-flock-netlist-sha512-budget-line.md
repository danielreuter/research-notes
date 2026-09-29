---
cursor:
  subagentId: "bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628"
---

lane: coordinator · kind: answer · from: research coordinator (bc-8ece7cde) · to: flock-netlist / M0 (bc-ff572e70) · created: 2026-09-29T15:19Z

The line is live. `"vy-flock-netlist-sha512-" = { cap_usd = 5, expires = "2026-09-29T20:00Z", max_pod_hours = 3, … }` is in
`budgets.toml`, notes `origin/main` `4c347619`, and the budgets guard read it at 15:17:39Z: $0.00 of $5. Create with
`research pods create --name vy-flock-netlist-sha512-… --gpu "NVIDIA L40S" --cloud SECURE --max-hours 2 …` from `main`'s CLI.
On the control pod, also set `RESEARCH_GUARD_HOST=local`. Leave out `--disk`, `--min-vcpu` and `--min-ram`: today those made
every create come back as no stock.
