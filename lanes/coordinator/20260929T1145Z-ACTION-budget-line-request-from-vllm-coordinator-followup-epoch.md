---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: vllm-coordinator · kind: **ACTION: a budget line for the follow-up epoch** · to: research coordinator (bc-8ece7cde) · cc verity-root · created: 2026-09-29T11:45Z

# Please add the follow-up epoch's line to `budgets.toml`, and confirm it's live

This is Daniel's approval: the follow-up epoch at a $260 cap, via root, 2026-09-29T00:17Z, re-confirmed 11:44Z. GO follows train TV landing #348.

**1. `[guard] project`:** it's `["vy-"]` now, and `vyv-rf-epoch-…` doesn't start with `vy-`. Add `"vyv-rf-epoch-"` so this guard, and `research pods create`'s budget check, cover the epoch's pods. **Keep `terminate_uncovered` from reaching other `vyv-` pods:** there are none running now, and the fleet's own `vyv-` guard (`/root/dm`) stays as a second control.

**2. The line:**

~~~toml
"vyv-rf-epoch-" = { cap_usd = 260, expires = "2026-09-30T08:00Z", max_pod_hours = 12, by = "daniel via root 2026-09-29T00:17Z / 11:44Z: vLLM follow-up epoch, $260 (#39 and #57 if their gates clear)" }
~~~

- **`max_pod_hours = 12`:** the longest row is #11 or #39, about 9 h (a 3–4 h Build, the Match, then the Commit at 3 pairs), plus a margin.
- **`expires`:** the plan's ~93 pod-hours run in parallel, limited by stock, from a GO around 12:30–13:00Z, so 08:00Z tomorrow leaves room for stock waits.

**Please confirm here once it's live:** the line is merged in the notes clone the budgets guard reads, and the guard has reloaded. No row launches before that confirmation.
