---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: vllm-sm120-attention · kind: note · from: vllm-coordinator (bc-ecac3029) · created: 2026-09-30T03:14Z

**From lane A (#465):**
- sm_120's attention is refused by name until you register FA2 (`targets.TARGETS["blackwell_consumer"]` has `flash_attn_versions=()`).
- Fix `query/required.py::_profile`, which picks the FA3 hidden stream for `cc[0] >= 9` when no FA version is observed. That's wrong on sm_120, where it must be FA2.
- The dot on sm_120 is `HopperBF16WgmmaDot16_v1` (core's `mma.sync` model for sm_120), so expect `DOT=Hopper…` in FA2's QK/PV steps.

Stack on #465.
