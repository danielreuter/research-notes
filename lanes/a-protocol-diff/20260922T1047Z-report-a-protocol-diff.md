---
id: r20-proof/a-protocol-diff/20260922T1047Z-report-a-protocol-diff
campaign: r20-proof
lane: a-protocol-diff
kind: report
status: closed
repo: verity-main@f96fc53
origin: verity-main@f96fc53:backends/numerical/reports/a_protocol_diff.md
---

# a-protocol-diff: why the Rust verifier rejected a-gpu2's proofs at `LogUp POW level 2`

Lane `a-protocol-diff` (track A), 2026-09-22, branch `lane/a-protocol-diff` from `main` 2943ae0.  Question: Candidate
A's GPU prover (`backends/gkr/gpu`, a-gpu2, merged 2e1ef3f) accepts its own proofs; the independent Rust verifier
(`backends/gkr/verifier`, a-verifier, switched to `X^6 - 22` in 2943ae0) rejects them at `LogUp POW level 2: final
check` for B = 64 and B = 4096 (run r20260922-102428-2285, proofs `r20260922-101240-8f71/proof64.bin`, `proof.bin`
sha256 `3534476010f4…`).  Which side deviates from the written protocol?

## Findings

### F1. First differing quantity: the coordinate order of `rho` inside `eq(rho, x*)` at LogUp level 2 (prover changed the schedule; the verifier followed a-gpu's)

**Where.** Per-table fractional-sum GKR, level `k = 2` (the first level whose `eq(rho, x*)` has two factors).  Every
other quantity of levels 0-2 -- `q_root`, `lambda_0`, every round message `h`, every challenge `r`, the four claims
`p0, p1, q0, q1`, `mu`, `lambda'`, `g = p0 q1 + p1 q0 + lambda q0 q1`, `running` -- is **byte-identical** between the
Python verifier and the Rust verifier for `proof64.bin` (traces: `verify --trace-logup`, run r20260922-104038-eabb,
`rust_trace64.log` / `py_trace64.log`; the Python trace is a re-derivation of `gpu/logup.py::verify_table` with the
same prints).  Level 2 of the POW table:

~~~text
rho (a-gpu2, low-bit-first) = [mu_1, r_1]       x* = [r'_0, r'_1]
  eq(rho, x*) * g = [1006239379,1846182954,669164154,86163199,1148435643,1587069787] = running   ok
rho (a-gpu / Rust <= 2943ae0)  = [r_1, mu_1]
  eq(rho, x*) * g = [2009957947,1809695149,297570831,737626364,818801215,427211323] != running   REJECT
~~~

So transcript absorb order, labels, byte encoding, message order within a level, `lambda`/`mu` derivation, the
small-level path and the eager-vs-packed `eq` weights are all **not** the cause: challenges and messages agree.
Levels 0 and 1 pass on both sides because `eq` of zero or one coordinate does not depend on the order.

**Why.** a-gpu2 moved LogUp onto a-packed2's kernels (`gpu/logup_packed.py`, `packed/logup_reference.py`), whose
sumcheck binds the **low** bit of the level index first (round `i` pairs `(2y, 2y+1)`), so the next level's point is
`rho' = [mu] + x*` (`mu` on bit 0).  The a-gpu prover (v2e, c4d472a) and the Goldilocks crate `src/logup.rs` bind
the **top** bit first with `rho' = x* + [mu]`.  The two are the same protocol under bit-reversal of the level index
(same message count and order), but the message *values* differ from level 2 on, and the leaf point `rho_T` differs
by a reversal.  The Rust verifier was written from `PROTOCOL.md`, `gpu/README.md` and the a-gpu source; neither
document fixed the variable order, so it took a-gpu's (a latent assumption a-gpu happened to satisfy).

**Which side deviated from the written protocol.** Neither text pinned the order: `PROTOCOL.md` 4.2 / 5.1 step 2c
specified the identity, the degree and the message order but not which bit a round binds (it is not a soundness
matter -- any fixed order is a correct sumcheck -- but it is a transcript matter).  The prover-side claim was wrong:
`gpu/README.md` and the a-gpu2 merge / ledger said "transcript identical to a-gpu / v2e", and the Python verifier's
acceptance seemed to confirm it.  It confirmed nothing: `gpu/prover.py::verify` calls `gpu/logup.py::verify_table`,
which lives in the same module as the prover's reference `prove_table` / `leaf_claim_top` and was **edited together
with it** to the new order (its docstring says so: "the verifier here follows the new schedule").  Shared-code
verification cannot see a schedule change; the independent verifier did, exactly as intended.

**Decision.** The a-gpu2 change is sound (a bijective relabelling of the hypercube; both leaf-claim conventions are
converted at the boundary) and deliberate (documented in `logup.py`, `packed/README.md`), and it is what the 1.79 s
prover runs on, so the protocol text is updated to the low-bit-first schedule and the Rust verifier follows it:

* `backends/gkr/PROTOCOL.md` 4.2 gains "Variable order of the per-layer sumcheck" (round `i` binds bit `i`;
  `rho' = (mu_k, x*)`; leaf point handed over top-bit-first, i.e. reversed); 13.4's "verbatim" sentence excepts it.
* `backends/gkr/verifier/src/verify.rs::verify_table`: `rho = [mu] ++ x*` during the walk, reversed at the end
  (`SplitEq` / `eq_table` are top-bit-first); `verify --trace-logup` prints every level's operands **and** the value
  the other pairing would give, so the next drift of this kind is a one-line diagnosis.
* `backends/gkr/gpu/README.md`: the "transcript-identical to v2e" sentence corrected.

The Goldilocks crate (`src/logup.rs`) keeps its order: it proves and verifies its own transcripts (`fixtures/`) and
is not run against GPU proofs.

### F2. The Python verifier is not independent evidence for the LogUp schedule (shared helper)

`gpu/prover.py::verify` -> `gpu/logup.py::verify_table` and `logup.leaf_claim_top`, both in the prover's module; the
prover's GPU path (`logup_packed.py`) and its torch reference (`logup.prove_table`) and the verifier were switched to
low-bit-first in one edit.  Also shared with the prover: `field.eq_point`, `field.eq_table`, `field.interpolate`,
the transcript.  Any convention these encode is invisible to the Python round trip.  The Rust verifier shares none
of them (`verifier/README.md`), which is why it -- and only it -- caught F1.  Not a bug in the Python verifier, a
limit on what its `verified: true` means; the ledger's "independently verified" flag must come from the Rust run.

### F3. `PROTOCOL.md` 5.1 step 2c lists `mu_k, lambda_k` before "k rounds of sumcheck"; the implementations draw them after the four claims that *end* a level

Same transcript, different bookkeeping: the text's level-`k` block is (four claims of level `k-1`, `mu, lambda`,
`k` rounds); the code's is (`k` rounds, four claims, `mu, lambda`).  Both put `mu_k, lambda_k` strictly after the
four claims they combine, which is the constraint 5.1 states.  Not changed; noted so nobody "fixes" one to the other.

## Gate (fixed verifier 887fc5c, vy-g5: H100 80 GB + Xeon Platinum 8480+, `--threads 16`)

| check | result | run |
|---|---|---|
| `proof64.bin` (B = 64, r20260922-101240-8f71) | accepted, 0.148 s | r20260922-104038-eabb |
| `proof.bin` (B = 4096, sha256 `3534476010f4…`) | accepted, 3.37 s | r20260922-103843-37e5 |
| fresh B = 4096 proof from this tree (`--warmup 1 --reps 3 --proof-out`) | byte-identical sha256 (`3534476010f4…`); accepted x3: 3.57 / 3.26 / 3.28 s (16 T, median 3.28; linear test 3.05-3.35 of it); 1 T: 49.5 s | r20260922-104038-eabb |
| `mutate --sample 300` at B = 64 | **1320/1320 rejected** (message 300, ligero_w 300, ligero_qc 300, column_value 192, merkle_sibling 192, merkle_root 32, message_count 2, statement 2); mean 0.032 s | r20260922-103843-37e5 |
| negatives (`gpu.run negatives /workspace/bb/neg --proof-dir`, this tree) | Python: 52/52 rejected (8 at witness generation, 44 `assertions phase-2a: round 0 sum mismatch`); **Rust: 44/44 proof files rejected** (`epilogue/assertions phase-2a: round 0 sum mismatch`) | r20260922-104038-eabb |
| prover (this tree, B = 4096, 3 reps after 1 warm-up) | 1.875 / 1.779 / 1.924 s -> **median 1.875 s**; lookup 0.42, arith 0.65, open 0.54-0.66, commit 0.10; peak 47.9 GB | r20260922-104038-eabb |

The A e2e row (prover median 1.875 s + Rust verifier 3.282 s + 438 x RTT + 33.9 MB / 10 Gb/s, `verifier/e2e.py`):
RTT 0 / 1 / 10 / 50 ms -> **5.185 / 5.623 / 9.565 / 27.085 s**, verifier share 63 / 58 / 34 / 12 %; in
`backends/gkr/verifier/results_e2e_a_protocol_diff.json` and the ledger entry (`ledger/a-protocol-diff.jsonl`,
`seconds_per_vu` = 5.185 / 4096).  Compared with the a-verifier row (4.43 s a-gpu prover + 3.02 s verifier, 7.47 s
at RTT 0), the prover halved and the verifier is now the larger term.

## Open items

* The Rust verifier on the pod's 8480+ is 3.3 s at 16 threads (linear test 93%: `a`-vector fill 16 s + row NTT 32 s
  of CPU time); the a-verifier lane's 12-thread EPYC number was 3.0 s.  The verifier, not the 1.9 s prover, is now the
  larger half of e2e compute at RTT 0.
* `src/logup.rs` (Goldilocks) and the GPU protocol now differ in a documented way; if the Goldilocks crate is ever
  pointed at GPU proofs, its LogUp walk must be reversed as in `verify.rs`.
* a-verifier F1 (the committed a-gpu kernel path at c4d472a rejected at level 0 by *both* verifiers) is a different
  phenomenon (a fractional sum that is not zero), owned by a-verifier-2 on vy-sp1; not touched here.
