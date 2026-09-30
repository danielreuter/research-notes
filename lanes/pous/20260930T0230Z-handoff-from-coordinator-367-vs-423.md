---
cursor:
  subagentId: "bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628"
lane: pous
kind: handoff
from: coordinator
created: 2026-09-30T02:30Z
---

# coordinator -> POUS (cc verity-root): #367 is out of TW6; its test expects `circuit.SCHEMES == ("ncp-v2",)`, which #423 changed

- **What failed:** TW6's recorded check (r20260930-005547-1617) failed one `verity-vllm` test, and the failure reproduces locally:

  ~~~text
  integrations/vllm/tests/protocol_options/test_protocol_options.py::test_beside_sampled_proofs_pouw_is_admitted_for_ncp_v2_only
  E  assert ({'ncp-v2': 'w...4': 'shift24'} == ('ncp-v2',)
  ~~~

- **Why:** #367 `79241b7d` asserts `circuit.SCHEMES == ("ncp-v2",)` (line 433), and its `protocol_options` changes read `SCHEMES` as a
  tuple. #423 `618c0628`, which lands first, makes `circuit.SCHEMES` a mapping that includes `ncp-v1-shift24` → `shift24`. The two
  merge cleanly as text but not in meaning.
- **What I did:** I rebuilt TW6 without #367, as TW6b = TVD2's re-checked tree + #442 `b132b7f8` + #364 `7b1ba73f` + #423 +
  #454. The protocol-options tests pass there, and its check launches on `vy-coord-t6`.
- **What to do:** update #367 for #423's `SCHEMES`: the test, and `protocol_options/__init__.py` and `interface.py` wherever they
  assume a tuple. Stack it on #423, run `integrations/vllm/tests/protocol_options`, and send me the new head. It rides the next
  train. It touches `integrations/vllm`, so it goes after the per-test cache, which is TVC2, now re-checking.
- **The #380/#391/#372 stack** is still waiting for the circuit red team's grants on `9298a197`, `81a80d29` and `dcb83d0e`.
