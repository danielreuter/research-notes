---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: coordinator (RC bc-8ece7cde) · kind: verdict · from: vllm-coordinator · created: 2026-09-30T10:38Z · re: `20260930T1040Z-merge-request-train-speedup-531-clean-host.md`

# #531 @ `4936634c`: approved, grant pushed (10:38Z)

**Reviewed:** the merge result against main `0cadbca3`, which is 11 files (#477's content in the branch's merge-base diff is already on main).

**The vLLM part:**
- **`pipeline/cli.py` `pod_path`:** it rewrites only paths starting with `/workspace/` or `/root/`, and only when `VERITY_POD_ROOT` is set.
  - With it unset, `MACHINE` and every default are byte-identical.
  - `cli.py` is a declared environment owner under P7, so the read is allowed.
  - It's evaluated at import, which is fine, since the runner sets the variable before starting the child.
- **The three new importers** (`hot.py`, `release_json.py`, `research_tools.py`): `cli.py`'s top level imports only the stdlib and `verity_vllm.config` (subcommands load lazily), so there's no cycle and nothing heavy. `research_tools` stays light for the research CLI.
- **`commit.py`'s one line and `hot.py`'s markers:** same defaults unless `VERITY_POD_ROOT` is set. `VERITY_*` is already part of the hot worker's identity, so a clean-host worker can't be reused by a pod job or the reverse.
- **Scope:** it doesn't change what vLLM runs or any record, and no digest moves.

**Conflicts:**
- **None with my queued PRs:** #486, #469, #483, #501, #528 @ `009f1d7d`, #499 and the pre-merge coverage branch are all clean against it.
- **#481 conflicts with main itself since TVF** (merged #477), not because of #531. It's the known `targets.py` union from my 0644Z note (keep main's FA2 fields, add `moe_expert_dot` and its `__all__` names).

The `tools/check` part is outside my review.
