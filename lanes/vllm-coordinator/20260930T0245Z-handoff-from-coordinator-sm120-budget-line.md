---
cursor:
  subagentId: "bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628"
lane: vllm-coordinator
kind: handoff
from: coordinator
created: 2026-09-30T02:45Z
---

# coordinator -> vLLM coordinator (bc-ecac3029): the `vy-sm120-` budget line is live

- **The line:** `"vy-sm120-" = { cap_usd = 60, expires = "2026-10-08T00:00Z", max_pod_hours = 4 }`, approved by Daniel via root at
  02:38Z for the sm_120 port's capture pods on RunPod RTX PRO 6000. It's committed to research-notes `budgets.toml` at `d0adc285`.
- **Reloaded:** the budgets guard read it at 02:39:46Z (notes `f3edd424`): `'vy-sm120-': $0.00 of $60`. Both the guard's parser and
  `main`'s accept the file.
- **For your four port lanes:** name each pod `vy-sm120-<something>`, and pass `--max-hours 4` or less to `research pods create`.
  The line covers all of Oct 7 (UTC). Ask for a raise or extension here if the captures need it.
- **Your PRs:** they come through my trains; file each merge request in `lanes/coordinator/`. They touch `integrations/vllm`, so they
  go after the per-test cache (TVC2, re-checking now) unless you mark one urgent. Each gets the cheap checks (merge on `main`, the
  wall-clock lint) before it joins a train.
