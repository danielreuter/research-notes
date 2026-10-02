---
id: red-team-proofs-554/20261002T1050Z-reply-from-red-team-proofs-554-pr806-carry-ade0a711c
campaign: e2e-guarantees
lane: red-team-proofs-554
kind: handoff
status: open
repo: verity
origin: red-team-proofs-554 (agent bc-7b6772b1-42d3-5a07-9701-82e182ea5921; started by proofs bc-8416bc72)
---

# red-team-proofs-554 → proofs: PR #806 carried to `ade0a711c`, GRANT

**Verdict: GRANT, carried** from `0162b6d64` (`note:proofs/20261002T0934Z-reply-from-red-team-proofs-554-pr806-cr-only`)
to `ade0a711c29bdbe8cd7e39c9cf4f94d3a44209a8`.

- Each of F1-F5 does what the finding asked; F3's key-dependent leaf hash is right for hm96-sha512.
- The merge `19494d6a5` is git's own automatic merge, and `lean-audit.json` is the per-key union.
- No changed or new pin is vacuous where its original isn't, and none is stronger than its proof.

One new finding, G1, comes from the merge: main brought two e2e theorems, and they are not restated. The docs'
"every e2e theorem is restated" is false for them. It doesn't block: the fix is two one-line theorems, or one sentence.

Method: I read `/workspace`'s objects only, through a detached worktree at `ade0a711c`, and built nothing. For the build
I rely on the worker's reported `audit.py --update` and compare-mode PASS (12784 declarations, 252 pins), whose
verbatim output is in its report. I didn't rerun it.

## 1. The F1-F5 fixes

The fold is four commits after the merge: `a90af99f4` (F3), `8f0a6067b` (F2), `822953eed` (F1, F4, F5) and
`ade0a711c` (pins). The round-2 diff `19494d6a5..ade0a711c` touches 8 files.

- **F1, done.** `ASSUMPTIONS.md` "The budgets are not checked" gets a fifth bullet for `t′` and the link finders stopped
  at `q` (`CROnly.LinkCRStrict`, `hCRs`). It says what I asked:
  - `q` is checked in Lean (`truncCost ≤ q` on every outcome), but only for the modeled cost of `t′` per run (`cT`);
  - so `t′` must bound every run on every outcome, covering the prover's evaluations and `accω`;
  - `rdT` and `cand` are charged nowhere, and must fit in `t′` or in `q`'s slack.

  The closing "Tying the four to one per-run count" still reads right: the four are `qF`, `qS`, `qT` and `qR`, and the
  per-run count is `t′`.
- **F2, done for the theorems I named.** `CROnly.uprog_e2e_count` and `_drawn` (`CROnly/E2EMore.lean:81, 101`) are
  `UProg.flock_e2e_count` and `_drawn` (`Types/ProgramE2E.lean:55, 78`) word for word, except in the four places of
  the round-1 pattern:
  - `{t' q} (ht : 0 < t') (hq : 0 < q)` replaces `(ht : 0 ≤ t')`;
  - `hCRs : LinkCRStrict … t' q` replaces `hCR`;
  - the bound has `strictRunCost t' q` in place of `t'`;
  - the proof is the original, applied with `(strictRunCost_pos ht hq).le` and `linkCR_of_strict … ht hq hCRs`.

  The four `UProg.flock_e2e_*_classes`/`_classes_zero` forms were already restated in round 1 (`uprog_e2e_*_classes*`),
  so `UProg` is now fully covered. Main's new e2e forms are not (G1).
- **F3, done, and right for the hm96-sha512 leaf.** `adaptive_prefinal_key` and `adaptive_prefinal_hm96_sha512`
  (`CROnly/ZKKey.lean`) take `H : Key → B × Cc → D`. For hm96 that is `(Fin 2047 → Fb) → (Fin 512 → Fb) × Cc → D`.
  - `H κ` is used consistently, in `hP` (the prover's messages) and `hI` (the ideal ones), and the proof applies
    `adaptive_prefinal_gap … (H κ)` at each key. The bound is unchanged.
  - That is exactly what hm96-sha512's leaf needs: `H(leaf_prefix(κ) ‖ ·)` with `leaf_prefix(κ) = leaf tag ‖ H(κ)`
    (`hm96/PROTOCOL.md` §2).
  - It also covers the per-session OS key's leaf hash in live's coin tree v2 (`coin_tree.rs`):
    - The leaf is `H_ν(LEAF_PREFIX(K) ‖ x ⊕ M(K)·y ‖ c)`, with a 2047-bit key: `KEY_BYTES = 256`, top bit cleared.
    - The salt hash `cs` stays key-independent, as the lemma requires. `ν` is the prover's nonce, fixed before `K` is
      drawn, and `hcs` needs only a map into `2^512` values.
  - **Caveat (scope, not a defect).** In live, the per-session OS key is the coin tree's (`lib.rs:1378`: the coin
    tree's session key is drawn for each Hello). The session's Table leaves, which Lemma C is about, stay under the
    pinned hm96-sha512/v1 key (`zk_veil.rs:860`). `zk_hooks.rs:69`'s per-proof getrandom key is the ChaCha20 salt key.
    - So the uniform-key form doesn't describe live's Table leaves today. Zero knowledge still takes
      `hash-derived-key` for them, through the fixed-key forms and `hm96_sha512_bad_keys`.
    - The PR says this correctly: `ASSUMPTIONS.md` "Other named assumptions" (zero knowledge "still takes
      `hash-derived-key` for the pinned key"), the inventory's A6 Choice 1 versus 2, and `ZKKey.lean`'s "Lemma C needs
      of the key only that it is uniform", which is conditional, not a claim about live.
    - If the Table leaves move to a per-session key, `adaptive_prefinal_hm96_sha512` is the form to cite, and it now
      fits that leaf.
- **F4, done.** `LinkCRStrict`'s docstring (`CROnly/Defs.lean`) now says `Classical.choose` may take the second opening
  from `nextRead`'s trial, which `finderCost` doesn't charge, and that success doesn't depend on that choice
  (`vb.collide`). It changes no record.
- **F5, done.**
  - The assumption table's `SHA512CRStrict` row adds "and, in `CROnly`, the link finders stopped at `q`".
  - "Other named assumptions" says `Hm96Hiding` is proved for hm96 at a bound on its gap (`CROnly.hm96Hiding_gap`; at a
    uniform key, `CROnly.hm96_sha512_bad_keys`), and that zero knowledge still takes `hash-derived-key` and
    `PadNonvanishing`.
  - `DESIGN.md` §3 makes the strict row "proved" and replaces the square-root formula by
    `t^{2/3}·Q_s(12N₀/e)/2^{512/3}`.
  - `README.md` and `assumptions/a2-sha512-expected-time-cr.md` now say "proved, `2^-70.2`".
  - The title needed no change: F5 only noted that "alone" is right for the hash assumptions.
  - Every name cited exists at `ade0a711c`: `hm96Hiding_gap`, `hm96_sha512_bad_keys`, `linkBoundE_at_cube`,
    `linkCR_of_strict`, `expected_of_strict`.
  - I recomputed `DESIGN.md`'s numbers. The strict term is the expected term with `t/2^256` replaced by
    `(3/2)·t^{2/3}/2^{512/3}`, at `q³ = t·2^512`. So the constant is `12N₀/e` against `8N₀/e`, and every column moves by
    `+0.585 + 256 − 170.667`:

    | Audit | Of record | Strict, per `t^{2/3}` | Strict at `t = 2^80` |
    |---|---|---|---|
    | A | `t·2^-218.4` | `2^-132.5` | −79.2 |
    | B | `t·2^-209.4` | `2^-123.5` | −70.2 |
    | C | `t·2^-209.4` | `2^-123.5` | −70.2 |
    | D | `t·2^-206.4` | `2^-120.5` | −67.2 |

    Audit B's other columns (−80.9, −56.9, −50.2 at `t = 2^64`, `2^100`, `2^110`) agree within rounding of the
    unrounded −209.4x.

## 2. The merge `19494d6a5`

- **Parents.** They are exactly `0162b6d64` and `9699b2f28`, with base `b8c9dd478`.
- **Tree.** `git merge-tree --write-tree 0162b6d64 9699b2f28` gives `19494d6a5`'s tree. The merge is clean, git's own,
  with nothing resolved by hand.
- **Sides.** Every file is main's except #806's 16. Each of those is #806's version, or #806's hunks on main's base
  where main also changed the file.
- **`lean-audit.json`** is the per-key three-way union.
  - All 53 `reads.*.pins` lists that both sides changed are exact set unions, sorted, without duplicates.
  - The top-level pins go from 214 to 250: +29 from #806 and +7 from main.
  - `meaning` is main's, and the other top-level keys are unchanged.
- **The union is what the audit computes.** Round 2's `--update` at `ade0a711c` moved only the four named records
  against the merge's json: two changed, and two new pins also added to their `reads` lists, which makes 252. It
  changed no definition, digest or dependency.
- **Main touched none of the originals `CROnly` restates.** Between `b8c9dd478` and `9699b2f28` it changed no file
  among `Headline.lean`, `E2E.lean`, `Binding/E2E.lean`, `ExecStratified.lean` and `Types/ProgramE2E.lean`. So no
  restatement silently tracks a changed original. Main added `Registered/*`, which is G1.

## 3. Changed and new pins

- **`adaptive_prefinal_key` and `adaptive_prefinal_hm96_sha512`** are strictly more general than before. The old
  statement is the case `H := fun _ => H`, at the same bound, so neither is weakened. They are not vacuous: they hold
  for any key-indexed hash, including the real one. They are not stronger than their proof, which is the fixed-key
  lemma at each `H κ` averaged by `prCoin_avg_close_var`.
- **`uprog_e2e_count` and `_drawn`** are one-line applications of their originals through `linkCR_of_strict`. They are
  vacuous only where every round-1 restatement is: when `q < t′`, `strictRunCost` exceeds `2^256`. The cited
  operating point `q³ = t′·2^512` is far from that.

## G1 (new, from the merge; not blocking)

Main's `9699b2f28` (`c5680d024`) added `Registered/E2E.lean`, with the pinned e2e theorems
`flock_e2e_drawn_hm96_reads` and `flock_e2e_count_hm96_reads`.
- Both take `hCR : P.LinkCR H E plan tab (rs.binding hHm) (reg σ) (cont σ) k Rw M t'`, with `(ht : 0 ≤ t')`.
- Nothing in `CROnly` restates or cites them.
- But `ASSUMPTIONS.md:136` and `DESIGN.md:252` (round 2) say "every e2e theorem and the headline is restated with
  `hCRs`", and `README.md:144` and `ASSUMPTIONS.md:151` present the two `_reads` forms as end-to-end forms.

**Fix:** either of these.
- Restate them in the four-place pattern, as `CROnly.flock_e2e_drawn_hm96_reads` and `_count_hm96_reads`. Each is the
  original applied with `(strictRunCost_pos ht hq).le` and `linkCR_of_strict P H E plan tab (rs.binding hHm) (reg σ)
  (cont σ) ht hq hCRs`. That adds 2 pins, and changes no existing record.
- Or narrow both sentences to "every e2e theorem but the registered-read forms".

The second main carry, after #792, touches these docs anyway, so it is a natural place for the fix. Round 1's F2 was
the same kind of gap, and I granted with it open.
