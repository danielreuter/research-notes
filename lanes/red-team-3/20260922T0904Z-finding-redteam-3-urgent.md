---
id: r20-proof/red-team-3/20260922T0904Z-finding-redteam-3-urgent
campaign: r20-proof
lane: red-team-3
kind: finding
status: closed
repo: verity-main@f96fc53
origin: verity-main@f96fc53:backends/numerical/reports/REDTEAM_3_URGENT.md
---

# red-team-3: ACCEPTED forgeries (urgent, for the coordinator)

Lane `red-team-3`, worktree `lane/red-team-3` (rebased on main 147a6f8). Harness: `backends/redteam/logup-b`
(`redteam-logup-b battery`), run r20260922-085839-3976 on vy-cpu3, BabyBear^4, 2 real VUs (`vu-k1536-neg`),
2^17 rows, FRI (blowup 2, 8 queries, pow 1 -- the PCS parameters do not matter for these two classes).

## U1. B-AIR **LogUp** realisation is statement-unbound (F1 class) -- ACCEPTED

`verity_direct::lookup_stark::verify_lookup(config, air, challenger, proof, preprocessed)` takes **no public values
and no statement**. A proof of a batch of two all-zero VUs (a = b = 0, y16 = 0) verifies as "the proof of" the two
real VUs (words 48849, 16299) -- or of any other 2-VU statement. The claimed words live only in the committed
`vu.claim` trace column; nothing outside the trace is absorbed into the transcript or checked at zeta.

* Case `zero_batch_as_any_statement`: prover trace = zero VUs, verifier = real statement -> **ACCEPTED**.
* The `lane/soundness-fixes` fix (statement digest as public values, `stark.rs::verify_bound_bytes`,
  `statement.rs`) touches **only the limbs path** (`stark.rs`, `main.rs`); `lookup_stark.rs` is untouched, so when
  that lane merges the LogUp numbers on the ledger (`vu_bench_lookup`, `--lookup`) remain unbound.
* Severity: **critical** for any LogUp-path result claimed as a proof; the B-AIR LogUp bench numbers are
  timing-only until fixed.
* Fix (owner: soundness-fixes / b-lookup): port `Statement` binding into `prove_lookup`/`verify_lookup` -- absorb the
  statement digest (words, B, field, layout id, table ids + `total_rows`) into the challenger before `pre_commit`
  is observed, expose `vu.y16` (and the operands with `--bind-operands`) as public columns checked at zeta exactly
  as `verify_bound_bytes` does for the limbs path.

## U2. B-AIR LogUp: `degree_bits` is read from the proof (F2 class) -- ACCEPTED

`verify_lookup` sets `degree = 1 << proof.degree_bits` and only checks `preprocessed.height() == degree`. The
verifier in `main.rs::vu_bench_lookup` hands it `pre.clone()` -- the **prover's** padded table matrix -- so the
height check is against a prover-controlled value. A verifier configured for log_n = 19 (4096 VUs) accepts a
2^17-row proof.

* Case `degree_bits_from_proof` (verifier builds the table at `1 << proof.degree_bits`, as `main.rs` does) -> **ACCEPTED**.
* Case `degree_bits_pinned_by_pre_height` (verifier builds the table at its own 2^19 rows) -> REJECTED
  (`InvalidProofShape`). So the fix is one line in the verifier's contract, not in the AIR.
* Severity: **high** (a small batch proves a large statement's row count); compounds U1.
* Fix (owner: soundness-fixes / b-lookup): `verify_lookup` must take `log_n` from the verifier's configuration
  (statement B) and reject `proof.degree_bits != log_n`; `main.rs` must build `pre_for_verify` from
  `tables.preprocessed(1 << cfg_log_n)`, never from the prover's matrix.

Everything else in the T1 battery so far REJECTS (out-of-table query with an exact adversarial helper ->
`OodEvaluationMismatch`; see `note:r20-proof/red-team-3/20260922T0921Z-report-redteam-3` for the full table when the run completes).
