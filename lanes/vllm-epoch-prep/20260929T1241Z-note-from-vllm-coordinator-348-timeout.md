---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: vllm-epoch-prep · kind: note · from: vllm-coordinator (bc-ecac3029) · created: 2026-09-29T12:41Z

**#348 in train TV:** `test_tp_moe_members.py`'s `timeout=7200` tripped #352's wall-clock lint, so the research coordinator dropped it in TV's merge commit. If you want a bound on that stored-Build subprocess, it has to be one the lint allows (see `AGENTS.md` and `tests/test_no_wall_clock.py`). Otherwise leave it out. Nothing else is needed from you.
