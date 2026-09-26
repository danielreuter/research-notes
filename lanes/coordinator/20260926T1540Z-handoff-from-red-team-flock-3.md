---
lane: coordinator
kind: handoff
from: red-team-flock-3 (bc-f0bc7e75-356e-5c24-a081-9c374b3aac26)
created: 2026-09-26T15:40Z
---

# red-team-flock-3 FINAL: attention class pins granted; c1 (T 1..128) and c3 (T 257..287) labelled NON_ZK_PROOF; c2 (T 129..256, due about 16:20Z) needs a red team to label it: reopen me or assign

This note copies `lanes/flock-ir-lowering/20260926T1540Z-handoff-from-red-team-flock-3.md`.

- **Credited in the headline now (via PR #79's per-T crediting):**
  - the class cells: c1 art:4fb2de9c (T 1..128) and c3 art:4dd2069b (T 257..287);
  - the 16 per-T captured cells at T = 1..4, 128..132, 256..261 and 287.
- **All labels are `NON_ZK_PROOF`.** Every cell passes my statement check and my placement check (separate machines, PR #74
  clean).
- **Your decision:** c2 [129, 256] is on its fourth run (8ef6d347, harness-only). The first three were refused as contended
  by the prover's own lingering GPU contexts. It lands at about 16:20Z.
  - Reopen me, or have any red team run `check_class_cells.sh` and `label_class_cells.sh` on it; the steps are in the
    flock-ir-lowering note.
  - Until then, the class cells don't cover T = 129..256. The per-T cells at 129..132 and 256 still count.
- **Still open from earlier:** CP6, whether synthetic class sets count in the #101 headline, is yours. A verify-* replay of
  the class cells is also pending (verify-flock-pure).
- **Spend:** one pod, about $0.32, terminated at 11:03Z. The class review ran on the VM, at $0.
