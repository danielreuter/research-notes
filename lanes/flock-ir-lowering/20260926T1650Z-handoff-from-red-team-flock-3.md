---
lane: flock-ir-lowering
kind: handoff
from: red-team-flock-3 (bc-f0bc7e75-356e-5c24-a081-9c374b3aac26)
created: 2026-09-26T1650Z
---

# red-team-flock-3 FINAL: class cell c2 (T 129..256, art:b61eafa9) checked, placement-separate, labelled NON_ZK_PROOF. With c1 and c3, class pins now cover T = 1..256 and 257..287; CP6 is recorded as a note for Daniel

This follows `20260926T1540Z-handoff-from-red-team-flock-3.md`. The report is
`lanes/red-team-flock-3/20260926T0958Z-report-red-team-flock-3.md`, in its FINAL section.

- **c2:** art:b61eafa9 (the clean re-run at 8ef6d347, which is harness only and inside the grant).
  - The verifier's `class.json` is byte-identical to the manifest I generate.
  - All 128 sub-batches pass `cell_check.py`, and `key_counts` = the verified T (129..256, 2,048 heads).
  - Placement is separate: pair b, machines pxp3jjc5ozkz and daejz5pkfg8j, with different boot ids and a routed 10.x
    link; PR #74 is clean.
  - Main's `key_class_of` credits all 128 T.
  - Labelled `NON_ZK_PROOF`. The duplicate registration art:ef10f5fb was not labelled, on the coordinator's instruction
    (16:34Z), since verify-flock-pure replays b61eafa9.
- **All three class cells:**

  | cell | class | T | heads |
  |---|---|---|---|
  | c1 art:4fb2de9c | [1, 128] | 1..128 | 2,048 |
  | c2 art:b61eafa9 | [129, 256] | 129..256 | 2,048 |
  | c3 art:4dd2069b | [257, 512] | 257..287 | 496 |

  Each has `proof_class NON_ZK_PROOF` and a `finding` by red-team-flock-3. Main's PR #79 credits each listed T at that T's own
  throughput.
- **CP6 (for Daniel's decision list, as a note and not a blocker):** synthetic class sets (the spine generator's draws for T
  outside #101's 16 captured values) count in #101's headline, as the FP8 cells' synthetic spine sets already do. The render
  footnotes the input provenance. This was the coordinator's ruling at 15:37Z, and all three class cells' findings carry it.
- **Evidence:** art:8be608c6 (the class-pin review), art:3b34c1dd (the c1 and c3 checks) and art:f5935b64 (the c2 check and
  placement).
