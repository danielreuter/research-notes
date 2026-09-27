---
lane: coordinator
kind: handoff
from: verify-flock-pure
created: 2026-09-27T12:15Z
---

# verify-flock-pure: M0's GEMM art:4a80e8cb and attention art:02cb7df9 are verified=accepted as file re-verifications; timings check out against the recorded runs; replayed on the VM CPU, no pod, $0

- **Run:** replay run r20260927-114642-b2fa, a local `research run`, rc 0 and preserved.
  - An earlier local run, r20260927-114157-7023, was stopped by me after one ill-posed negative: it flipped the record's own
    `config.require_link`, which the replay never trusts. Its replays were identical, and nothing was labelled from it.
- **Build:** lane/verify-flock-circuit @ c9324a77, which is flock-netlist e226a920 (the cells' verifier commit; it contains the
  EX2 clamp 855fe81f and the device witness b84d2606) plus a `replay` subcommand for flock-circuit. That subcommand is the
  library's own offline path, `Server::from_record` plus `finish`, together with `replay_coin_seed`. `62-circuit-replay.sh`
  drives it.
- **Pins and bindings:** the circuit, MUFU tables and public files were staged here from the input sets with circuit_bench's
  public-only staging. For each cell, the circuit SHA-512, the public files, Σ and the ANDs per instance equal the verifier
  pod's, the prover's and the result's.
- **Sessions:** every recorded session replays under this host's statement, with the step-0 coin derivation replayed from the
  revealed seed.
- **Negatives:** these were all refused on both cells: another session's proofs, swapped reps, a changed seed, a changed mid
  coin, changed retained round bytes, a changed link Σ, a changed link point, the link exchange removed, and another circuit.
  GEMM also refused another point's public file.
- **Timings:** each result's t.total is the median of its prover run's 5 timed e2e. The verifier's own clock corroborates
  each e2e (session_s − verify_s). ands.count equals B × the ANDs per instance, recomputed here.

| cell | result | circuit SHA-512 | sessions accepted | median e2e = t.total | unit-AND/s |
|---|---|---|---|---|---|
| GEMM K=2048, 1,024 coordinates | art:4a80e8cb | cecaa76a… | 12/12 | 16.362 s (15.98–16.48) | 69.08 M (1,024 × 1,103,744 ANDs) |
| Attention T=129, 16 heads | art:02cb7df9 | 2b2e9603… (EX2 clamp) | 6/6 | 2.917 s (2.66–3.09) | 51.65 M (16 × 9,416,316 ANDs) |

- **Checked, no finding:** the recorded record's `config` block is informational. The replay uses the verifier's own
  configuration, and flipping that block doesn't change the verdict.
- Recorded coins are replayed, so this is not transferable evidence.
