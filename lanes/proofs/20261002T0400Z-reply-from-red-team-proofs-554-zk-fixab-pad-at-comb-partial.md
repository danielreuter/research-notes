---
id: 20261002T0400Z-reply-from-red-team-proofs-554-zk-fixab-pad-at-comb-partial
campaign: overnight
lane: proofs
kind: reply
status: open
repo: verity
origin: red-team-proofs-554 (started by proofs bc-8416bc72)
---

# bf16-hill's `--zk` verifier speedups at `5b6682463`: Fix A GRANT, Fix B GRANT WITH CONDITIONS

Reviewed `cursor/bf16-hill-zk-fixab-1d95` at `5b66824638ef8f61ff0cb5d52cd18bd4d312a84a` (origin's head when I wrote this), its
three commits on the folded accepted head `5a299de4e`: `56b6dc3eb` (Fix B, `FC_ZK_LINCHECK`), `63e4b43f4` (Fix A, `zk::pad_at`
in the prover and the verifier, superseding `446a069e7`) and `5b6682463` (the zk default becomes `partial`). CPU only, on this
VM, in a detached `/tmp` worktree. Evidence: `art:bb94bd585b7b2aff4e597bd9ea798e6e9ff2f389124142167fbbd5379b086894`
(`findings.md` has the derivations and every number).

## Fix A, `pad_at` in place of the whole padding codeword: GRANT

`pad_at` computes exactly `pad_codeword`'s values at every position the verifier can read, for every shape `--zk` produces.

- **Derivation.** `pad_codeword` encodes `(c·ybar ‖ 0 ‖ ybar ‖ 0)` in the novel basis. Since `X̂_{L+i} = Ŵ_{log_msg}·X̂_i`, the
  value at `q` is `(c + Ŵ_{log_msg}(q))·Σ ybar_i X̂_i(q)`. That is what `pad_at` evaluates, with the same helpers
  (`eval_sk_at_vks`, `evaluate_scaled_basis_inplace`, `next_s`) M0's induced-basis verifier already trusts at production
  size.
- **Shapes.** Every `--zk` shape is m = 25..35 with level-0 rate 1, `log_msg` 12..22 and `t_pad` 436..554. The domain is the
  standard additive subspace (no coset), and the field is F128, with F256 handled by coordinates.
- **Exhaustive check.** I compared the two at every position of every one of those shapes, at its `t_pad` and at `t = 1024`,
  plus small shapes over every `t` and rates 1–4: 34,387,928 positions, 0 mismatches. That includes all 8,388,608 positions at
  m = 35.
- **Author's test.** It passes, and so do `exact::`'s two tests. Note that it covers nine shapes, all with `log_msg ≤ 9`, so
  none of production's. Adding m = 25's shape costs 0.02 s; recommended, not a condition.
- **Call sites.** `enforced_extra` now gets one `pad_at` value per query instead of indexing the full codeword. The values and
  their order are the same, so proof bytes and the verifier's sum are unchanged.

## Fix B, M0's structured `comb_partial` under `--zk`: GRANT WITH CONDITIONS

No zk layout can satisfy the predicate while `comb_partial` computes something different.

- **Same predicate, function and inputs as M0.** The zk replay takes the structured path under M0's own predicate. It calls the
  same `comb_partial_structured` on the same circuit object and the same weights, inner point, rounds and β as M0's default
  verifier.
- **Masks and extra lanes never enter `comb`.** `comb` is the public circuit structure times the coins. The masked level 0
  and the extra lanes live in the Ligerito opening after the lincheck. The mask slot is part of the same block circuit in M0
  and in zk.
- **The transcript doesn't depend on the mode.** `comb` is never absorbed.
- **Runs.**
  - The structured path is really taken under `--zk`, so `both` compares something real.
  - `--zk` selftests on RoPE d64 and GEMM k64 at m = 25 and 26: every case gets the same verdict and the same refusal reason
    under `both`, `partial` and `flat` (41 and 42 cases). No refusal anywhere says the two combs differ.
  - Offline re-verification under all three modes: accepted every time.
  - A scratch zk-aware lincheck-modes case, with honest proofs and proofs whose lincheck `z_partial` or first round was
    altered: the same verdicts and reasons in every mode on four statements. The altered proofs are refused by the zk inner
    proof's batched constraint.

**Condition.** `lincheck_modes_agree` is the selftest case that claims "flat, partial and both: the same verdict on honest and
altered lincheck proofs", and it does nothing useful under `--zk`:

- It re-encodes a zk proof without its `InnerProof`, so every altered set fails to decode.
- It never sets `FC_ZK_LINCHECK`.
- So it fails on every `--zk` statement, and every `selftest --zk` reports `all_pass: false`.

This predates the branch: the code is identical at `5a299de4e`. But now that `partial` is the zk default, this is the case
that should guard it. Land a zk-aware version: my 14-line scratch diff in the art is one, and it passes on four statements.

Minor, not a condition: unlike M0's lincheck, the zk replay doesn't check `n_cols` or the inner point's length against the
layout. They agree by construction; an assert would make that local.

## For both fixes

- **No gate runs these tests.** `check` never runs flock-live's `cargo test`: `check_build.sh` only runs `cargo check` on
  `flock-circuit`. So the `pad_at` test, which PROTOCOL §5 cites, and `exact::` run in no gate. Until something does, the
  merge handoff should record their pass at the merged commit.
- **The author's evidence isn't in the store.** The profile run `r20261002-030908-4848` has no outputs there (`result` and
  `run_files` are null), so the 4,317-position and 12-rep claims can't be checked from the store. My art covers Fix A at every
  production shape and Fix B at m = 25 and 26 on real sessions. A real m = 35 session under `both` is still only the
  author's unstored claim.

Labels by `red-team-proofs-554`, `--ref note:proofs/20261002T0400Z-reply-from-red-team-proofs-554-zk-fixab-pad-at-comb-partial`:
`grant red-team` and a `finding` on the art, and a `finding` on `r20261002-030908-4848`. I left `grant` off the profile run
because I verified the fixes, not its timings.
