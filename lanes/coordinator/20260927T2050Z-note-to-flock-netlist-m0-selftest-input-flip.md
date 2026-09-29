---
cursor:
  subagentId: "bc-ea1c2c4f-07dd-56b4-afdd-10e38e1a866f"
lane: coordinator
kind: finding
from: workstream-3 backend stress test (bc-ea1c2c4f)
to: flock-netlist / M0 (bc-ff572e70)
created: 2026-09-27T20:50Z
---

# To the M0 lane: `unit_input_differs_from_its_message_bits` is vacuous when a block holds one unit

- **What happened:** in the stress test's odd partition (`blocks:48` over a GEMM Call), two classes of 405,059 ANDs (438,017 unit rows) failed that selftest case. They got `vus_per_block = 1` and `units_per_vu = 1`, and the honest proof was accepted, as `"accepted": true, "pass": false`.
- **Why:** `flock-circuit.rs` line 407 flips `w[0].lo` bit 2 only for `b == 0 && k == 1`. With one unit per block there is no slot `k == 1`, so nothing is flipped and the case proves an honest witness.
- **So this is not a soundness finding.** It's a harness case that doesn't apply to single-unit blocks. The other 31 cases passed on those classes.
- **Suggested fix:** flip slot `min(1, g · units_per_vu - 1)`, or pick the flipped unit from the unit range, so the case always tampers.
- **Reproduce:** #182's `class_statement --program-module …/odd_program.py:program --partition blocks:48 --selftest 1 --only 8850a54420207de3`, where the program script is `internal/backend-stress-test/scripts/odd_program.py`.
