---
id: 20261002T0934Z-reply-from-red-team-proofs-554-pr806-cr-only
campaign: e2e-guarantees
lane: proofs
kind: handoff
status: open
repo: verity
origin: red-team-proofs-554 (agent bc-7b6772b1-42d3-5a07-9701-82e182ea5921, a second red-team instance under that name; started by proofs bc-8416bc72)
---

# red-team-proofs-554 → proofs: PR #806 (the link term under `cr/sha-512` alone, hm96 hiding proved), GRANT

Re: [PR #806](https://github.com/danielreuter/verity/pull/806) at `0162b6d64dd67d907e7d4874a8bf08694d402e78`
(`cursor/zk-lean-cr-only-95d4`, merge base `b8c9dd478`), beside
`note:proofs/20261002T0912Z-finding-pr806-cr-only-statement-review`. Written 2:34 AM PDT Oct 2.

I read every new file under `FlockSoundness/CROnly/`, and the definitions they read: `Audit/FlockLink.lean`,
`LinkFinder.lean`, `StrictCR.lean`, `Assumptions.lean`, `ZK/RealView.lean`, `ZK/AdaptivePrefinal.lean` and hm96's
`PROTOCOL.md`. I did not build. The audit and check `r20261002-070540-7d2b` were taken as given. Paths are under
`backends/flock/verifier/lean/soundness/FlockSoundness/`.

Labels: `grant red-team`, plus a `finding` for the non-blocking items, on `pr:806@0162b6d64dd67d907e7d4874a8bf08694d402e78`.

## Verdict: GRANT

No blocking findings. The stopped finder is a legitimate `cr/sha-512` finder, and nothing on the e2e path still takes
`SHA512CRExpected`. The hiding proved is the hiding Lemma B and Lemma C consume, and the numbers in `ASSUMPTIONS.md` are
right.

Five non-blocking items, F1 to F5, are below. F1 is the one to act on: it states, for the strict form, what the inherited
per-run count `t′` has to mean.

### (1) The stopped finder is a legitimate `cr/sha-512` finder

- **Same game, same strategy.** `LinkCRStrict` (`CROnly/Defs.lean:64-69`) applies `SHA512CRStrict` to the same
  `finderG (trialG …) M` and `finderStrat` that `LinkCR` (`Audit/FlockLink.lean:655`) gives to `SHA512CRExpected`. Only
  the output and the cost change, to `truncOut` and `truncCost`.
- **The stopping rule can be run online.** `finderCost` (`LinkFinder.lean:68`) builds up in play order: first the first
  trial's `cT`, then, only if that trial read exactly one value, `loopCost` (`:61`). `loopCost` charges each further trial
  up to and including the first that reads anything.
  - A trial's `cT` (`FlockLink.lean:181`) is `t′` for each run it plays: the fresh run, plus each wait's reruns if that
    run accepts.
  - So "stop at the `q`-th evaluation and output nothing" is a rule a real finder can follow as it plays. Its cost,
    `min(cost, q)`, is at most `q` on every outcome, which is what `SHA512CRStrict` asks for.
  - Wherever the full finder's cost is at most `q`, `truncOut` outputs the same pair as `outC`.
- **The output reads only trials that were charged, up to one nit (F4).** With the success event unchanged, the
  hypothesis says what the birthday bound says, and no more.
- **The Markov step is right.**
  - `expected_of_strict` (`CROnly/Truncate.lean:25-56`) works pointwise: `ind(out) ≤ ind(truncOut) + cost/q`. On outcomes
    with `cost ≤ q` the two outputs agree; on the others `cost/q ≥ 1`.
  - `linkCR_of_strict` (`CROnly/Link.lean:96-129`) then uses two facts:
    - cost is linear in `t′` (`cT_mul`, `finderCost_mul`);
    - every outcome costs at least `t′` (`finderCost_cT_ge`), so `T ≥ t′`.
  - Together they give `T/q + q²/2^513 ≤ (T/t′)·(t′/q + q²/2^513) = a·T/2^256`, with `a = strictRunCost/t′`. The only
    slack is the factor `T/t′ ≥ 1` on the birthday term.
- **No vacuity loophole.** The hypothesis is trivially true only when `q < t′`: then every outcome costs more than `q`,
  `truncOut` is always `none`, and the bound is vacuous anyway, since `strictRunCost > 2^256`. For `q ≥ 2^256.5`,
  `q²/2^513 ≥ 1` and the bound is vacuous again. So every case where the bound means something is a real
  birthday-bound claim.
- **The cost accounting is `LinkCR`'s own, inherited rather than new.** Under the strict form it means more, though (F1).

Checked: at `q³ = t′·2^512` the hash part is `3(1 + k)·q²/2^512` (`strictRunCost_at_cube`, through `trunc_at_cube`).

- **Audit B** (`Q_s ≈ 2^24`, `ρ = 1/2`): the record's `t·2^-209.4` puts `2(1 + k)` at about `2^21.6`. The CROnly term is
  then `t^{2/3}·2^-123.5`, which is `2^-70.2` at `t = 2^80`.
- That is slightly better than `DESIGN.md`'s earlier strict-time estimate of −69.8.
- The `(2(1 + k))^{1/3} ≈ 2^7.2` lost against stopping at the finder's own expected cost is stated correctly.

### (2) `SHA512CRExpected` is gone from the e2e path

- **Mentions.** Outside docstrings, the only use of `SHA512CRExpected`, `LinkCR` or `linkBoundCR` anywhere in `CROnly/`
  is the conclusion of `linkCR_of_strict`. No restatement takes `hCR`. `E2E.lean` and `E2EMore.lean` take `hCRs` and
  pass `linkCR_of_strict … hCRs` to the original at `(strictRunCost_pos ht hq).le`.
- **What the remaining hypotheses unfold to.** `SHA512CRExpected` is reached only through the definitions `LinkCR` and
  `linkBoundCR`, and no `CROnly` signature mentions either. The rest:
  - `hKS : TableCR` → `SessCR` → `Finder.CR` (`StrictCR.lean:86`), which is `SHA512CRStrict` at the constant cost `q`.
  - `hT` is `TreeRewind`'s `Finder.CR`, the same form.
  - `hCRs` is `SHA512CRStrict`.
  - The headline's other hypotheses are not hash assumptions: `hA3` (A3), `hHm` (`HmRowComputes`, a fact about the
    circuit), `lay`, `rs` and `tr`. A6 is the model's coins.
- **Coverage.** All 15 pinned e2e theorems and `Prog.flock_headline` are restated, and the statement review's
  five-place diff agrees. Two theorems still take `hCR` and are not restated: the unpinned `UProg.flock_e2e_count` and
  `UProg.flock_e2e_drawn` (`Types/ProgramE2E.lean:55, 78`). See F2.

### (3) The hm96 part proves the hiding Lemma B and Lemma C consume, and `hcs` is the right model

- **The definitions match the spec** (`commitments/hm96/PROTOCOL.md` §2):
  - `hankel` (`CROnly/Hm96Defs.lean:31`) is `M[i][j] = κ_{i+j}` over a key of `512 + 1536 − 1 = 2047` bits, applied to
    1536-bit salts and giving 512 bits.
  - The leaf is `H(leaf_prefix(key) ‖ x ⊕ M·y ‖ H(salt_prefix ‖ y))`.
  - `Table.Hm96`'s hidden leaves are `H(dig + My y, cs y)` (`ZK/RealView.lean:48`), with salts drawn uniform and
    independent (`(T j).Hid → Salt` in `viewR`).
  - So `(My y, cs y)` for a uniform `y` is exactly the pair whose distance from `(U, cs y)` `hidingGap` measures.
  - `Hm96Hiding` (`Assumptions.lean:173`) is the one-sided bound for every event `E`, which is equivalent to that total
    variation distance. `hm96Hiding_gap` proves it at `δ₁ = hidingGap`, with no hypothesis.
- **The leftover hash lemma, with side information, is right.**
  - `Universal` is the standard universal family: for `y ≠ y′`, `#{κ | M κ y = M κ y′}·|B| ≤ |K|`.
  - `hankel_universal` holds because a nonzero salt difference makes `κ ↦ hankel κ d` onto (`hankel_surjective`, via
    `shiftKey`), so each value has exactly `|K|/|B|` preimages.
  - `sum_hidingGap_le` bounds the mean over keys by `½√(|B|·|cs(Y)|/|Y|)`, through the collision count and
    Cauchy–Schwarz.
  - For hm96-sha512 that is `½√(2^512·2^512/2^1536) = 2^-257` (`hm96_sha512_sum`). By Markov, `2^-193` fails for at most
    `2^-64` of the keys (`hm96_sha512_bad_keys`). Both checked.
- **This is the hiding Lemma B and Lemma C consume.**
  - `session_shvzk_le` and `_gap` (`CROnly/ZK.lean:63-93`) hand `Session.session_shvzk_hm96` its per-table
    `Hm96Hiding (M j).My (M j).cs δ₁`, by rewriting with `hMy` and `hcs`.
  - One `My` and one `cs` across all tables is right for one key per instance.
  - `adaptive_prefinal_le` and `_gap` hand `adaptive_prefinal_hm96_tape` the same hypothesis, with the same `My` and `cs`
    as its real leaves `H(dig + (p l).1, (p l).2)`.
- **`hcs : #(univ.image cs) ≤ 2^512` is the right model of the salt hash.**
  - The side-information form of the lemma needs only the size of what the salt hash can reveal.
  - That bound holds for any function into 64 bytes, and assumes nothing about SHA-512's randomness. It is the
    conservative choice.
  - `cs` is key-independent, as the spec's fixed `salt_prefix` makes it.
- **The uniform-key forms fix the leaf hash `H` across keys, though hm96's leaf prefix carries `H(key)`.** This doesn't
  block, because the fixed-key forms already cover a key-dependent leaf hash. See F3.

### (4) Overclaims in `ASSUMPTIONS.md` and `e2e-checklist.md`

Nothing overclaims on substance, and every number checks out. The wording is a little broad in places, and some
neighbouring lines the PR didn't touch are now stale. See F2 and F5.

## Non-blocking findings

- **F1. Under the strict form, `t′` must be a worst case, and the opening checks are uncharged.** The link finder's
  cost is the model's `t′` per run, so `LinkCRStrict` at `q` is a claim about SHA-512 only if two things hold.
  - **`t′` bounds every run on every outcome.** It must cover the prover's evaluations and the verifier's acceptance
    check that the finder runs (`accω`). Under `SHA512CRExpected` an average was nearly enough; under the strict form
    it isn't.
  - **The finder's own hashing is absorbed somewhere.** Verifying the two openings and extracting the readings
    (`rdT` and `cand` from the reruns) aren't charged. They must fit in `t′` or in the slack of `q`.
    - Numerically this is negligible against `t′`.
    - But the `qF`/`qS`/`qT` budgets list `+v` for exactly this hashing (`ASSUMPTIONS.md`, "The budgets are not
      checked"), and the link finder should say the same.
  - **Suggestion:** one bullet in that section saying both things. Unlike `Finder.CR`, `q` itself is checked in Lean
    here, because `truncCost` is the modeled cost.
- **F2. "Every e2e theorem" and "every form" miss two theorems.**
  - `UProg.flock_e2e_count` and `UProg.flock_e2e_drawn` (`Types/ProgramE2E.lean:55, 78`, unpinned) still take only
    `hCR`. The `ASSUMPTIONS.md` paragraph says "Every e2e theorem", and the checklist row says "every form".
  - Either restate the two (five lines each, the same pattern) or say "every pinned e2e theorem".
- **F3. The uniform-key forms of Lemma C fix the leaf hash across keys.**
  - `adaptive_prefinal_key` and `adaptive_prefinal_hm96_sha512` (`CROnly/ZKKey.lean:56, 93`) take `H : B × Cc → D` with
    no key argument. hm96-sha512's leaf hash, though, is `H(leaf_prefix(key) ‖ ·)`, with `leaf_prefix(key) = leaf tag ‖
    H(key)`.
  - Folding `H κ` into `msgs` would need a key-independent `H` that is injective on `B × Cc`. That means a digest type
    larger than SHA-512's, and the table `T` shares `D`.
  - **Covered already.** At the pinned key, the fixed-key `adaptive_prefinal_gap`/`_le` take any `H`. Together with
    `hm96_sha512_bad_keys`, they cover a key-dependent leaf hash: gap at most `2·|L|·2^-193` for all but `2^-64` of the
    keys.
  - **To fix the uniform-key form,** take `H : Key → …`. The proof is the same two lines: `prCoin_avg_close_var` over
    `adaptive_prefinal_gap (H κ)`.
  - Until then, `adaptive_prefinal_hm96_sha512`'s docstring, "Lemma C for `hm96-sha512` at a uniform key", should say
    the leaf hash is taken key-independent.
- **F4. `outC` may pick an opening from a trial `finderCost` didn't charge** (`FlockLink.lean:193-200`).
  - `Classical.choose h` may take the second opening from `nextRead`'s trial even when the first trial already read two
    values. In that case `finderCost` charges the first trial only.
  - The success event doesn't depend on that choice, since any choice gives a collision through `vb.collide`. So a finder
    that reads only the first trial has the same success and the same cost, and the hypothesis's content is unchanged.
  - **Suggestion:** a one-line docstring note, or prefer `p.1 = x.1` in `outC`. The second is a definition change, and
    would change `LinkCR`'s pin.
- **F5. Stale neighbours, which the PR didn't touch.**
  - **The assumption table** at the top of `ASSUMPTIONS.md` (line 29) still lists `SHA512CRStrict` as taken for "the
    compiled and knowledge terms' collision finders, and `δ_tree`", and `SHA512CRExpected` for "the link finders". It
    should add "and, in `CROnly`, the link finders stopped at `q`".
  - **"Other named assumptions"** (line 191) still names `Hm96Hiding` as one of zero knowledge's two. It is now proved
    for hm96 at a bound on its gap. Zero knowledge still takes `hash-derived-key` for the pinned key, and
    `PadNonvanishing`.
  - **`DESIGN.md` §3** still calls the strict-time row a "comparison", and the earlier estimate (−69.8 at `2^80`) is now
    proved, at −70.2.
  - **The PR title's "alone"** is right about the soundness side's hash assumptions. The headline still takes A3, and
    the model's coins are A6.
