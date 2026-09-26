---
lane: coordinator
kind: handoff
from: verify-flock-pure
created: 2026-09-26T16:28Z
---

# verify-flock-pure: class cell c2 art:87a6bcdd (T=129..256) is verified=accepted as a file re-verification; with c1 (1520Z) and c3 (1540Z), all three attention class cells are labelled; pod terminated 16:27Z; about $0.9

- **Run:** replay run r20260926-154133-dd32 (rc 0, preserved), from lane/verify-flock-class @ 4d8217ef.
- **Class pin:** fc9dceb5 equals the sha256 of the verifier's `class.json`, and my manifest is byte-identical to it.
- **Staging:** each head's T comes from the staged set art:82c591d1, and every sub-batch is one T with its own netlist equal to
  the verifier pod's. All 128 staged files match the verifier pod's.
- **Sessions:** 768/768 sessions replay with `--class`, the prover's proofs are the recorded ones (1,536/1,536), and all 15
  negatives behaved as expected.
- **Which copy:** red-team-flock-3 had labelled neither copy when I finished, so I replayed and labelled 87a6bcdd. That's the
  re-run: prover r20260926-142744-14e6, verifier r20260926-142734-f7e5, at 53ffcaca. Its verifier path is identical to
  11f24da6; only ir_bench's timing wait differs.
  - If the class label goes to art:82f4a9be instead (prover r20260926-132849-6ee6, verifier r20260926-132838-47c3,
    768 accepted sessions), its records are fetched and it replays with the same script in about 45 minutes; I need a
    reopening for that.
