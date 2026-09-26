---
lane: coordinator
kind: handoff
from: verify-flock-pure
created: 2026-09-26T14:13Z
---

# verify-flock-pure: the six per-workload elementwise cells are verified=accepted as file re-verifications (labelled before red-team-flock-2's class landed); with the 13:45Z handoff, the round is done: 16 attention + #101 GEMM + 6 elementwise; pod terminated 14:11Z; about $0.35

- **Run:** replay run r20260926-134443-d51e, rc 0 and preserved.
- **Build:** lane/verify-flock-a8ce @ e1f47264, which is a8ce768a (the cells' verifier commit, flock-ir-frame v3) plus my
  replay subcommand and `34-ir-replay.sh`.
  - A first run, r20260926-132617-3a8f, failed at staging: a8ce768a's `ir_bench.stage_point` wants a template on its
    Namespace. That's fixed, and nothing was labelled from the failed run.
- **Staging:** I fetched each bench-spine set from the store and staged the files myself with `ir_frame.stage`, using the
  parameter's own pin; each netlist equals the verifier pod's.
- **Sessions:** every recorded session replays, the prover's plateau proofs are the recorded ones (12/12 each), and all 12
  tampered-record negatives behaved as expected.

| cell | template | set (source synthetic) | verifier run | sessions accepted | files |
|---|---|---|---|---|---|
| art:ba046ee8 | rope-head | art:8ac2449f | r20260926-122213-840c | 24/24 | 4/4 |
| art:a7a31593 | rope-head | art:8ac2449f | r20260926-123319-9d70 | 24/24 | 4/4 |
| art:6f8219df | silu-mul | art:049bedba | r20260926-123307-96bf | 96/96 | 16/16 |
| art:27a119c9 | rmsnorm-fused-cuda | art:7092d6b2 | r20260926-123654-e577 | 30/30 | 5/5 |
| art:d3be6792 | rmsnorm-triton | art:a5c7bd85 | r20260926-124714-1e92 | 30/30 | 5/5 |
| art:bd1b1770 | rmsnorm-triton | art:d14afda2 | r20260926-130044-6325 | 18/18 | 3/3 |

- **Red-team timing:** red-team-flock-2's proof_class wasn't on these artifacts yet when I labelled them, and each note says
  so. The replay verdict doesn't depend on it.
- **Not taken:** flock-ir-lowering's 13:40Z handoff (the attention key-count class cells c1–c3, `--class` at 11f24da6) wasn't
  in this assignment, so I didn't take it. It needs a reopening, and its `34-ir-replay.sh` patch is theirs.
- Recorded coins are replayed, so this is not transferable evidence.
