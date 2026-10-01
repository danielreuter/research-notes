---
id: 20261001T0212Z-handoff-from-proofs-arch-session-verifier
campaign: verity
lane: proofs-verify-overlap
kind: handoff
status: open
repo: danielreuter/verity
origin: proofs-arch (for @proofs, 5:52 PM PDT)
---

# proofs-arch changes `flock-circuit serve`'s verifier: phase timers in the verdict, and a template-aware lincheck by default

@proofs asked me to locate the session verifier's unattributed time and to put the template-aware lincheck into it. This
note lists what that changes under your fan-out work (FC_VERIFY_SERVERS × FC_VERIFY_AHEAD). Proofs, transcripts and
accept/reject don't change; only verify time and the verdict's extra fields do.

**Branch:** `cursor/proofs-arch-95d4`, head `b9b724e9d`. It merges your `556e40e39` (everything you'd pushed by 01:51Z) and
proofs-bf16-hill's `d1775df80` (`BlockCircuit.types` as `CscCircuit`). Nothing of yours is changed.

- **`CircuitVerifier::verify_circuit`** now calls `session_verify::verify_extra`, a new module that restates upstream's
  `verify_ligerito_extra` with timers. The pool layout is upstream's: a one-thread `flock-verify` pool (or
  `FLOCK_VERIFY_THREADS`) for the core and the opening, with the lincheck fold on the all-core pool.
- **`FC_LINCHECK=partial|flat|both`** (`serve` and `selftest`; any other value is refused). The default is `partial`: the
  lincheck's final value comes from the block's slot types, Δ and the pin, and no 2^k vector is built. `flat` is
  upstream's code; `both` computes the two and rejects on any mismatch. `partial` falls back to flat wherever upstream
  would panic.
- **The verdict** gains `record_clone_s`, and each `reps[i]` gains `timing`: `verifier_s`, `replay_squeeze_s`,
  `replay_finish_s` and `phases`. The phases are decode, regions, c0 check, bind, zerocheck, lincheck (its `lincheck_comb`
  parts and `lincheck_mode`), opening setup, opening (ring-switch, Merkle, residual, rest), other and total. The timers
  are wall clock in the verdict only, never in a proof or transcript byte. Your `verify_ahead_matches_serial` compares
  `session.json`'s streams, link and proof digests, so it doesn't see them. It passes, as do all 38 K=64 selftest cases.
- **The Merkle, ring-switch and residual timers** come from a new upstream patch, `flock-vtime-b684b12.patch`, applied after
  the zk patch in `60-circuit.sh` and `check_build.sh`. It adds thread-local nanosecond counters to
  `pcs/ligerito.rs` and `pcs.rs`, and nothing else.
- **New selftest case `lincheck_modes_agree`:** an honest session plus two altered lincheck proofs (`z_partial`, a round
  message), each verified in all three modes. It passes only if the verdicts and reasons agree, and the altered proofs
  are refused at `sumcheck-final`.
- **A finding for your fan-out:** the verifier pool is a process-wide one-thread pool, upstream's and mine alike. So
  `serve --concurrency` sessions in one process verify one at a time. Separate verifier processes, as in your
  `FC_VERIFY_SERVERS`, are the way around it; more sessions per process are not.

The K=2048 and K=8192 per-phase breakdown, flat against partial, will be in `note:20260930T2330Z-report-proofs-arch` once
node 1's job (112-127, one GPU) has run. If you merge my branch, `partial` is your default unless you set `FC_LINCHECK=flat`.
