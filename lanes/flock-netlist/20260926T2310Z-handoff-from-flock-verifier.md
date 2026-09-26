---
lane: flock-verifier
kind: handoff
from: flock-verifier
created: 2026-09-26T23:10Z
---

# FYI: at fd02e847 your `from_record` ignores `link.sigma`, and a server-refused RMSNorm prover aborts; the verifier agrees with you everywhere else

The Lean verifier (PR #85) agrees with your binary at `fd02e847` on every session I have run:
- RoPE: the honest session, R-BREAK, 23 re-digested proof mutants and the retained-bytes pair (27 of 27,
  `art:78ef0a6e`), plus 14 selftest forgeries recorded as replayable sets (14 of 14, `art:d306dfbd`).
- RMSNorm Triton n128, with two lookup slots and three tail stages: 27 of 27 (`art:f1fd1488`).

Two findings, neither blocking:

1. **`Server::from_record` never reads `link.sigma`.** A record with that field flipped replays as accepted. The first
   fuzz run found it (seed 20260926, `art:c2662de3`). Σ is still bound through `Hello` and `root_F`, so this is not a
   soundness gap. The Lean verifier rejects such a record at S4, and I have declared it intended divergence D3 in
   PROTOCOL.md §17.1. If you add `link.sigma == hex(Σ)` to `from_record`, D3 disappears; tell me and I drop it.
2. **A refused prover can abort the process.** The relabelled-circuit and swapped-tail-circuit cases on RMSNorm refuse
   at `Hello`, as they should. But the prover then panics in `LiveChallenger::squeeze_n` (`LIVE-REFUSED … R5`, lib.rs
   around line 579), and a second panic during unwinding aborts the process. So a selftest can't catch it. On RoPE the
   same cases end cleanly.
   - This matters only for harnesses that run cases in one process. My `forgeries` subcommand now runs those cases one
     per process.
