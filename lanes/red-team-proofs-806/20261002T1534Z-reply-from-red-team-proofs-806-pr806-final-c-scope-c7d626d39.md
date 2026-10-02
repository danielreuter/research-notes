---
id: red-team-proofs-806/20261002T1534Z-reply-from-red-team-proofs-806-pr806-final-c-scope-c7d626d39
campaign: e2e-guarantees
lane: red-team-proofs-806
kind: handoff
status: open
repo: verity
origin: red-team-proofs-806 (agent bc-7b6772b1-42d3-5a07-9701-82e182ea5921; started by proofs bc-8416bc72)
---

# #806 at `c7d626d39`: how it relates to `final_c'` (#793), and whether it calls `--zk` sound

**Verdict: GRANT carried at `c7d626d3975f5e62bc609f88fdce631fb39bd4ee`.** Every group is (c): none is about the `--zk`
session model, none is a soundness step for `--zk`, and nothing #806 lands calls main's `--zk` sound. #806 does not
depend on #793. Checked independently in a worktree at `c7d626d39` (merge base with main `818a4689e`), with no Lean
build: the diff since round 3 is docs only, and module docs belong to no declaration.

## 1. Each group

- **e2e forms and headline** (`CROnly/E2E.lean`, `E2EMore.lean`; 17 theorems) and **registered reads**
  (`CROnly/Registered.lean`; 2): (c). Every statement plays the audit on `batchedSession`
  (`Audit/FlockBatched.lean:58-59`, `(sessionB execArith H E (plan S R)).map (decide ∘ acceptedB …)`), as the originals in
  `E2E.lean`, `ExecStratified.lean` and `Registered/E2E.lean` do. That session's verifier evaluates `final_c` in the
  clear: `sessionB` → `TabSpec.after` → `tableAfter` → `repC` → `zerocheck` (`Model/Piop.lean:55-61`, `pc = Σ lagΛ·msg`),
  and the executable checks `pc == p.finalC` (`Flock/Piop.lean:84`). The import closure of `FlockSoundness.CROnly`
  (216 modules) contains no `Discharge/ZkSession` module, and `restZK`, the model that receives `final_c'` before the
  inner proof, is defined only in `Discharge/ZkSession/Algebraic.lean:361`. So no CROnly statement can mention the `--zk`
  model. The one `zk` token in the statements is `hzk : zer < kIn` (`E2EMore.lean:176,203`), a zero column's index bound.
- **hm96 hiding** (`Hm96Defs`, `Hiding`, `Hankel`, `Hm96Sha512`): (c). These are statistical facts about hm96's keyed
  hash (`hidingGap`, the leftover hash lemma, the Hankel family's universality, the hm96-sha512 mean and bad-key bounds).
  No verifier or session appears in them.
- **Lemma B and Lemma C** (`CROnly/ZK.lean`, `ZKKey.lean`): (c). `session_shvzk_le`/`_gap` give a two-sided `prCoin`
  bound between the view and the simulator. `adaptive_prefinal_le`/`_gap`/`_key`/`_hm96_sha512` give a `prCoin` gap
  between witnesses `w` and `w′` against any `V*`. Both are zero knowledge, not soundness. Outside their own files, no
  Lean source in `backends/flock/verifier/lean` uses any of their names, or `hm96Hiding_le`, `hm96_bad_keys`,
  `hm96_sha512_bad_keys`, `hankel_universal` or `hm96_sha512_tail` (`rg -w`). The only outside hits for
  `hm96Hiding_gap` and `hm96_sha512_sum` are a comment in main's `Discharge/ZkSession/Coins.lean:21-24`, in namespace
  `FlockSoundness.Discharge.ZkSession`.

**Observation (not a finding).** `Assumptions.Hm96Hiding`, which #806 proves, is an input to main's `--zk` soundness
coin step: `ZkSession.coin_fresh`, `coin_fresh_key` and `coinLeaf_fresh` take it as `hT1` (`Coins.lean:38,62,82`).
#806 doesn't compose its proof there, and `Session.lean:49-52` says composing it into the session needs a round-by-round
bound. Whoever does that later discharges a fact about hm96 that holds regardless of #793; it would not close
`final_c'`, which is case (a) in `Session.lean:46-48` and stays main's open item.

## 2. The diff `5e5e6d558..c7d626d39`

- One commit, 6 files, +28/−14:
  - `ASSUMPTIONS.md`, `DESIGN.md`, `README.md` and `assumptions/a2-sha512-expected-time-cr.md` (prose);
  - `CROnly/E2E.lean` and `CROnly/ZK.lean`, four added lines each, inside their `/-! … -/` module docs and before
    `namespace`.
- `git diff 5e5e6d558 c7d626d39 -- '*lean-audit.json'` is empty, so the record is the round-3 file (341 pins, the
  per-key union checked in `note:red-team-proofs-806/20261002T1452Z-reply-from-red-team-proofs-806-pr806-round3-5e5e6d558`).
- A module doc is part of no declaration's statement or definition, so no record can move. This matches the worker's
  plain audit at `c7d626d39` (PASS, 341 pins, no record differs).

## 3. No text calls main's `--zk` sound

I read every added line of #806 against main (`818a4689e..c7d626d39`, all `.md` and `.lean`, `lean-audit.json` aside),
grepping for `--zk`, `zk`, `ZkSession`, `final_c` and `sound`. I also checked the proposed title and the scope paragraph
(`internal/proofs/zk-lean-cr-only-pr.md`).

- Each soundness claim is scoped to the non-ZK session:
  - the `ASSUMPTIONS.md` **Scope:** paragraph;
  - `DESIGN.md` §3's "Strict time, proved" bullet;
  - `README.md`'s "proved for the non-ZK session";
  - the A2 note's "(not `--zk`'s, …)";
  - the `CROnly.E2E` module's **Scope.**;
  - the title's "the non-ZK e2e theorems and headline".
- Each `--zk` mention says `CROnly` restates none of `--zk`'s theorems, or that `final_c'` lies outside the ZK
  statements.
- The PR body's §3 Inventory lists the `--zk` path's open soundness guarantees. It claims none of them is proved.
- The added `sound` hits are `FlockSoundness` namespaces, plus "None is a soundness statement" (`CROnly/ZK.lean`).

**Nit (non-blocking).** Read without the bullet below them, three lines in `DESIGN.md` §3 don't name the session:

- the table row "Strict-time collision resistance alone (`cr/sha-512`, proved)";
- the log₂ row "Strict-time (proved)";
- the closing "`CROnly` replaces it there".

No `--zk` reading is possible, because `--zk`'s session takes the link term as an abstract `hlink` and uses no
`LinkCR` (`Session.lean:40`; PR body §3). If the worker touches the file again, "(non-ZK)" on those rows would make
them self-contained.
