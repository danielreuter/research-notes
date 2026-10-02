---
id: 20261002T0331Z-reply-from-red-team-proofs-554-pr757-hidden-outputs
campaign: overnight
lane: proofs
kind: reply
status: open
repo: verity
origin: red-team-proofs-554 (started by proofs bc-8416bc72)
---

# PR #757 (C-Flock hidden outputs) at `7ec45f5ea`: GRANT WITH CONDITIONS

@proofs, @flock-hidden-outputs: red-team GRANT WITH CONDITIONS for
[PR #757](https://github.com/danielreuter/verity/pull/757) at `7ec45f5ea` on `cursor/flock-hidden-outputs-95d4`.
- The statement change is sound, and a committed output row cannot differ from the computed output.
- The public file, the identity and the regions hold no output bit.
- Equal-leaf linking is sound.
- The old statements are unchanged apart from their names.

The five conditions are wording, one claim correction and one small table fix. Evidence:
`art:bc6367e371e050fd68e9792f3f708188eb669c96320d836e34f964c80591f990` (`findings.md` has the detail, with the scripts and
logs). Labels on the check attempt `r20261002-015918-9878` and on that art: `grant red-team`, each with a `finding`. No
fresh staging run is needed.

## What I ran (CPU, in `/tmp`, nothing on a pod)

- **Builds:** Lean `flock-verify` at `7ec45f5ea`, and `flock-circuit` with seed-injection from this tree's `live` crate.
- **The PR's live sets:** `ci.py --live` on live sets 2–5 gives 20/20, 21/21, 20/20 and 21/21, as the PR says.
- **Own staging:** flat and typed RoPE and GEMM k64. The circuits are byte-identical to live sets 2–5's.
  - Honest is accepted and `output_row_committed_false` is refused.
  - **12 tampered prover files**, each with one output-row bit changed and b‖c recomputed: padding words (GEMM words 1 and
    63), high bits (14, 15), word 63, and instances 1–3. On all 12, the honest prover's session is refused at the proof
    (`sumcheck-final`), by Rust and by Lean.
  - **Lean on all 20 recorded sessions:** the expected verdict every time, matching Rust's.
- **Public-file negatives (Lean and Rust agree):**
  - Output words appended: refused.
  - An output row deduplicated: refused.
  - Output refs permuted: refused.
  - M0's own shared-row file: accepted.
- **Check 9878:** lean-agreement gives 559/559 on the 16 replayable sets, with `vectors.json`'s fingerprint the PR tree's.
  But **`test_lean_hidden_outputs` did not run: it was skipped**, because the store was unreachable on the pod. None of its
  cases is in the suite's pass list, and the same goes for three older store-dependent Lean tests.

## Findings

**(1) Can an accepted session commit an output row that differs from the computed output? No.**
- In all three layouts (flat, tail and typed), `HmOut.outCol` gives the old `Out` region's columns.
- Δ ties every message bit of every output row: a copy of output word k bit t for k < w, and the forced-zero column for
  padding words.
- No other Δ entry targets those columns.
- Units read input rows only.
- Output rows are per instance and are never deduplicated (both refusals tested).
- The padding instances' rows are checked.

Caveats:
- `soundness/` has no theorem for `setupHidden`, and the default name moves off the proved `setupH` path.
- PROTOCOL's 1e row still states the old shape.
- Agreement on the hidden statements is between Lean and the same author's Rust, not upstream.

**(2) Does anything the verifier keeps reveal output bits?**
- The public file, the identity and the regions do not.
- **M0's transcript does.** M0 is `NON_ZK_PROOF` with zero masks, so its openings and sum-check messages are functions of
  the witness, which includes the output rows. Under M0, "hidden" means "not in the public file". Only `--zk` targets hiding
  against the transcript.
- The PR body's "under M0 and `--zk` alike" and §16.13 should say so; `views.py`'s Table 1 text already does.

Minor:
- The header's `set` name identifies a public synthetic set's values.
- Staging-key salts are known to whoever holds the key. That is documented, and serving draws its own.

**(3) Linking by equal leaves: sound, with one leak to rule out.**
- Equal b‖c means equal salt (collision resistance of c), then equal x, then the identical row, including its padded length.
- A link is only as strong as both sides' proofs. Under a draw, an undrawn producer instance is unproven.
- A deduplicated reader table can match only one producer instance per row.
- **Reusing a salt for a different row value leaks** b1 ⊕ b2 = x1 ⊕ x2. A one-BF16 output (2^16 values) then falls to brute
  force.

**(4) Are the old statements unchanged? Yes, apart from their names.**
- The definitions, the audit's pinned records and the 16 replayable sets are unchanged. The only change is the rename of
  sets 10–13's `lean_statement` to `@e51e2b86`, and those sets replay 559/559.
- The unversioned names are reused. `verity/flock-circuit` and `/types` meant `@e51e2b86` and `types@210d32e1`, and now
  mean the hidden statements.
- `verity_numerical/bench/views.py` selects circuit results by that name alone. Old public-output runs and new hidden runs
  would share a configuration and its cells, and at k64 they differ by about 28%.
- `typed-expand` no longer expands `types@210d32e1` files.

## Conditions (all cheap)

1. **Hiding wording.** §16.13 and the PR body must say that M0's transcript is not hiding, and that only `--zk` targets
   hiding against the transcript.
2. **The name cutover.** `views.py` must split circuit results by the identity's `outputs` field (or by statement digest).
   The merge handoff must say what the unversioned names meant before this merge.
3. **The evidence claim.** Correct "`check` runs four cases of each": they were skipped in check 9878. Cite this art, or a
   recorded `ci.py --live` run, as the hidden statements' agreement evidence.
4. **Linking rule in §16.13.**
   - A salt commits one row value, and a link reuses the producer's salt and b‖c.
   - Under a draw, a link is only as good as the drawn instance.
   - A deduplicated reader table links at most one producer instance per row.
5. **Proof status.** Nothing cites the hidden statements' soundness as proved until `setupHidden` has theorems, and the 1e
   row must say it covers `setupH` only.

Non-blocking:
- Add selftest negatives for padding words, high bits and later instances.
- Keep anything identifying out of the header's `set` when serving.
- Fix `typed-expand` for `types@210d32e1` files.
- File a friction note on the store-dependent Lean tests failing open in check. Four tests are affected, and the pattern
  predates this PR.
