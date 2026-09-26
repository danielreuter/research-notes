---
lane: flock-ir-lowering
kind: handoff
from: red-team-flock-3 (bc-f0bc7e75-356e-5c24-a081-9c374b3aac26)
created: 2026-09-26T15:40Z
---

# red-team-flock-3 FINAL: class cells c1 (T 1..128, art:4fb2de9c) and c3 (T 257..287, art:4dd2069b) checked, placement-separate, labelled NON_ZK_PROOF; CP2, CP7 and CP8 met; c2 is pending (your 8ef6d347 run, due about 16:20Z) with the commands to label it

This follows `20260926T1340Z-handoff-from-red-team-flock-3.md` (the class-pin grant). A copy is in `lanes/coordinator/`.

- **c1 and c3 are labelled `NON_ZK_PROOF`**, with a `finding` (ref r20260926-132829-2165). For each:
  - the verifier's `class.json` is byte-identical to the manifest I generate;
  - every sub-batch passes `cell_check.py`: 128/128 for c1 and 31/31 for c3;
  - `key_counts` equals the verified sub-batches' T: 128 T and 2,048 heads for c1, 31 T and 496 heads for c3;
  - placement is separate: pair b's machines are pxp3jjc5ozkz and daejz5pkfg8j, the boot ids, GPU UUIDs and drivers differ,
    the link is a routed 10.x address, and PR #74 is clean;
  - main's `key_class_of` (PR #79) credits every listed T (1..128 and 257..287) at its per-T throughput.
- **CP2 is MET at 11f24da6.** A non-canonical or duplicate-key manifest is refused (run r20260926-143204-b20f). **CP7 is
  MET** (main, PR #79). **CP8 is MET** (full-set points).
- **Commits after 11f24da6 are harness only:** 31d275ad, 53ffcaca and 8ef6d347. The verifier is the same, so they're inside
  the grant. Measurement note: 8ef6d347 excuses the prover's own exited GPU contexts in the timing guard. That touches the
  contention labels, not soundness.
- **c2 [129, 256] is pending, due about 16:20Z at 8ef6d347 on pair b.** Until it's labelled, T = 129..256 has no labelled
  class cell. To label it, a red team fetches the reference table from art:3b34c1dd (`class-ref-1-512.json`) and runs, from
  `lanes/red-team-flock-3/evidence/`:
  1. `check_class_cells.sh class-ref-1-512.json <c2 art>`;
  2. if it reports `CLASS_CELL_CHECK PASS`, `label_class_cells.sh <c2 art>`, which runs the placement check first.
- **Evidence:** art:8be608c6 (the review) and art:3b34c1dd (the c1 and c3 checks, placement, CP2). The report is
  `lanes/red-team-flock-3/20260926T0958Z-report-red-team-flock-3.md`, in its FINAL section.
