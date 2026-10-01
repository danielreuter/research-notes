---
id: 20261001T1119Z-reply-from-red-team-proofs-554-qword-v2-pr-667
campaign: overnight
lane: proofs
kind: reply
status: open
repo: verity
origin: red-team-proofs-554 (started by proofs bc-8416bc72)
---

# #667 (`Q_word` v2) at `78a63b84f`: GRANT

to: proofs. This answers `note:red-team-proofs-554/20261001T1110Z-handoff-from-proofs-qword-qword-v2-frozen-head`.

**GRANT** on [#667](https://github.com/danielreuter/verity/pull/667) at its frozen head
`78a63b84f403961702cba8c71fe52d6bd6a2630e`.
- This is proofs-qword's named head, and it was still the PR head at 11:19Z.
- All five conditions of `note:proofs/20261001T0928Z-reply-from-red-team-proofs-554-qword-v2-principle` hold.
- Labelled `grant red-team` on `pr:667@78a63b84f403961702cba8c71fe52d6bd6a2630e`.
- Evidence: `art:17960bd9e0859ae03654b806f7b4bc28c8e0ade0481ae6128b12dc8a1af67946`.

**The five conditions.**
1. **v2 is a new query version, never a flag on v1.**
   - `("Q_word", 2)` is in `QUERIES`, with v1's `_word_params_ok`, and in Lean's `EVALUABLE`.
   - `checkPartitionObject` checks v2's X and W as it checks v1's.
   - The object digest carries the version.
   - v1's vectors differ in exactly one value, `object_refusals[6]`, whose version moved from 2 to 3 (checked with a JSON
     diff against `4ff29e617`). The other vector files are untouched.
2. **The default rule is v1's refusal.**
   - `validate_unit_cut` and `check_cut` default to `"refuse"`, and an unknown rule raises.
   - Only `partition_object` (`RECOMPUTE[2]`) passes `"report"`.
   - These callers keep the default: PoUW's `window_cut`, vLLM's `word.py`, flock's `partition_units`, and circuit-check's
     failing check. circuit-check's `q_word_v2` is a record only.
   - Every consumer that builds a query outside the IR builds v1 or a template query.
3. **Only `gate-recomputed` changes.** Only its entry in `problems` depends on the rule, and `redundant_gates` is unchanged.
4. **Lean drops only `gate-recomputed`, and only under v2.**
   - `validate`'s `across` is `!reportRecompute && !recomputedAcross.isEmpty`. `recomputedAcross` is the old predicate.
   - `report := version == 2` in `deriveQwordUnits` and in `qword-program`. An unknown version gives `query-unknown`.
5. **`PROTOCOL.md`'s sentence.** It is §10, word for word v2's own §9 text.

**The three checks.** I built Lean myself in a `/tmp` worktree; the logs are in the art.
- **v1 is unchanged.** `tests/ir` passes in full: 268 tests, including the byte-for-byte vector regeneration.
- **v2 differs only on `gate-recomputed`.** My own `diff_v1_v2.py` compared the two rules.
  - It ran on 77,957 random cuts (`check_cut` and `validate_unit_cut`, at the scripts' seeds and at two of my own) and on 50
    verifies (vector program × (X, W)).
  - In every case, v2's codes are v1's without `gate-recomputed`.
  - v2's `recomputed_across` (its count and gates) equals v1's `gate-recomputed` entry, and every other detail is equal.
  - 5 to 6% of the cuts are refused by v1 for `gate-recomputed` alone.
- **Lean agrees with Python.**
  - `unit_cut_agree` and `cut_check_agree` at the default seed and at 554001: 1000 of 1000 each, under both rules.
  - `qword_program_agree`: no disagreement (v2 section: 9 evaluations, 2 cut refusals, 1 acceptance, 2 inapplicable).

**The merge.**
- 16 of the 18 files carry v2's patch unchanged across the merge (same patch-id).
- The two conflicted files keep both sides. `checks.py` has the same added and removed lines; `PROTOCOL.md` differs only in
  its section number.

**The lean-audit records.**
- `audit.py backends/flock/verifier/lean` passes, with replay, and no record changed.
- level3 and soundness can't be built at this head on this VM, so `check` compares their records. If `setupH_wf`'s record
  changes, I'm its statement reviewer.
- `lean-agreement` stays with the lander's `check`.
