---
cursor:
  subagentId: "bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628"
---

lane: vllm-coordinator · kind: handoff · from: coordinator · created: 2026-09-26T21:15Z

# Verdict request: PR #88 (salted-leaves, `hm96-sha256/v1` hiding leaves, opt-in on the vLLM host committer), head f1df809f

Daniel approved HM96 hiding leaves at about 19:58Z (`docs/project-context.md`). PR #88 touches:
- `integrations/vllm/verity_vllm/commit/` (`hiding.py`, `native_host.py`, `native_ranges.py`) and `acquire/committer_api.py`;
- the P10 size allowlist;
- `tests/commit/test_hiding.py`.

It's opt-in and off by default. Please confirm three things:
- the default path is byte-identical, so no digest of record moves;
- the ratchet lints pass on main plus #88;
- both range and point verification check the hiding layer.

A red-team review of the scheme (lane red-team-hm96) gates the merge too. I merge once both are in.
