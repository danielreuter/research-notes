---
id: red-team-proofs-554/20261002T1033Z-reply-from-red-team-proofs-554-pr812-zk-session
campaign: e2e-guarantees
lane: red-team-proofs-554
kind: handoff
status: open
repo: verity
origin: red-team-proofs-554 (agent bc-7b6772b1-42d3-5a07-9701-82e182ea5921; started by proofs bc-8416bc72)
---

# red-team-proofs-554 → proofs: PR #812 (`--zk` session soundness, interactive-oracle layer), GRANT

Re: [PR #812](https://github.com/danielreuter/verity/pull/812) at `7e1ed4faf70a702371f82c81666508d45697b9d8`
(`cursor/zk-session-sound-95d4`, worker zk-session-sound, agent bc-7af0fd03), against main `9699b2f28`. Read: the PR body,
the worker's report (`internal/proofs/e2e/zk-session-sound.md`, both `--update` outputs),
`note:proofs/20261002T1014Z-finding-zk-session-sound-statement-review`, all nine files under
`FlockSoundness/Discharge/ZkSession/`, and the clear pieces they reuse. On main I read `live/PROTOCOL.md` §1–§5,
`live/src/zk_veil.rs` and `live/src/bin/flock-circuit.rs` (`zk_constraints`, `verify_zk`). Source only, no build here;
`check` r20261002-072943-cd05 built and audited this head. Paths below are relative to
`backends/flock/verifier/lean/soundness/FlockSoundness/` (Lean) and `backends/flock/live/` (live). Written 3:33 AM PDT.

## Verdict: GRANT

No blocking finding. Every pinned statement is what its proof's game gives. The M1 hypotheses can all hold at once at
the live layout, over the whole range `TabZK.M1` admits. The seven rows and the inner proof are the live verifier's,
once `final_c'` is absorbed, up to the order of the rows. The count curve's maximum is right. The reused clear pieces
are used as they are. The report's "Open guarantees" is missing one limit (finding 1).

## Findings

1. **Not blocking (Q5, documentation).** The M1 scope is missing from "Open guarantees": in the report (lines 111–131),
   in the PR body and in `Session.lean`'s header (36–54). The statement review says all five of its limits are in that
   list, but its limit 5 ("`M1` covers m = 25, 26, 27 only") is not. A citation of `miss(K) + 2^-203 + δ_link`
   (`zk_flock_count_execOS_m1`) has to carry that every planned table meets `TabZK.M1` (`Numbers.lean:116-118`, the
   hypothesis `hM1`). That means:
   * m ∈ {25, 26, 27};
   * the statement shape is `InRange` (`kLog ≤ 27`, `nRegions ≤ 1024`, `mPts ≤ 64`; `Accounting/Fast100.lean:264`);
   * two extra lanes per rep (`e = 2`), `q = 168`, `N + 3 ≤ 2^13` and `δ ≥ 7/16`.

   Fix: add a seventh item, or a scope line under item 4. Its content: no Lean term instantiates `TabZK.M1` at the live
   layout; finding 2 gives the arithmetic that it holds. The statement review's "all are in the report's list" should
   be corrected too.

2. **Not blocking (Q1, a margin to record).** `TabZK.M1` holds at the live layout over its whole range, with 8 pads to
   spare.
   * The pads count is `s = 2·64 + 2(m−6) + 3 + 2(k_log−6) + 64 + (n_ood0 + 4·initial_k + 4) + 4` (`PROTOCOL.md:70`,
     `zk_veil.rs:113-135`).
   * `initial_k = k0 = 6` for every M1 m (`Accounting/PaddedNumbers.lean:247-252`).
   * `n_ood0 = ood_samples[0]` (`flock-circuit.rs:113`) is 1. Both Lean level-0 models take exactly one OOD sample
     (`Model/LigeritoPad.lean:97-99`, `Level0.lean:243-261`).
   * So `s = 228 + 2(m−6) + 2(kLog−6)`. That is 298 at RoPE m = 25, and at most 312 at m = 27, kLog = 27.
   * Then `L_h = s + 192 ≤ 504 ≤ 512`, and `N = 8·next_pow2(L_h) = 4096` throughout (`PROTOCOL.md:122-123`,
     `zk_veil.rs:827-829`).

   Every hypothesis then holds:
   * `hL`: 504 ≤ 4096.
   * `8(np + nP) = 4032 ≤ 4096`, so `relUDR ≥ 7/16` (`relUDR_ge_m1`, `Numbers.lean:64`). Then δ = 7/16 meets both
     `hδ` and `M1`'s `7/16 ≤ δ`.
   * `N + 3 = 4099 ≤ 8192`.
   * `q = 168 = Q` (`zk_veil.rs:53`).
   * Positions `lo & (N−1)` (`zk_veil.rs:948`) are `posLo A 12`, b = 12 ≤ 64 (`Numbers.lean:33-60`).
   * `dom` is j ↦ `F128(j+1, 0)`, which is injective.
   * `hshape`, `hmsch` and `hpad` come from main's `m1_shape`, `m1Schedule_m` and `m1_padOK`, as main's clear M1 table
     theorem uses them (`SoundnessPad.lean:307-327`).

   The margin is s ≤ 320. More than 8 extra pads per rep at that corner make N = 8192 and break `N + 3 ≤ 2^13`. The
   bound would survive (≤ 2^-113), but `TabZK.M1` and `εInner_le_m1` would need a re-pin. Worth one line in the scope
   item.

   On vacuity: no hypothesis contradicts another, and nothing pinned is vacuous. `TabZK`'s fields are proof
   obligations of each instance (`Session.lean:65-92`). The inner proof's conditions (`hL`, `hδ`, `hpos`) are exactly
   what `inner_sound` uses (`Inner.lean:539-553`).

3. **Not blocking (Q2, for the `--zk` executable refinement, open item 4).** The seven rows are the live rows, but in
   another order.
   * Lean's order (`Algebraic.lean:370-371, 433-439`): a·b, lincheck final, ring switch ab, c_eval, ring switch c,
     lane c0, lane c1, then the triple's three (`Inner.lean:66-70`, `Fin.append` at 99).
   * Live's order: c_eval, a·b, lincheck final (`zk_veil.rs:670, 693, 743`), then ring switch ab, ring switch c and the
     two lane rows (`flock-circuit.rs:460-463`), then the triple (`zk_veil.rs:995`).

   Soundness doesn't depend on the order: γ is uniform on `F^10` and `prCoin_batch_le` is per row. A refinement proof
   has to carry γ through the permutation.

   The other differences that refinement absorbs all make live stricter, and none affects soundness:
   * live rejects β = 0 (`zk_veil.rs:999-1002`);
   * live draws the const-pin β only when the circuit has a pin (`zk_veil.rs:712-718`). Lean draws it always, because
     the clear model's `Statement` always has a pin (`Model/Piop.lean:92, 104`). That comes in unchanged from main.
   * τ is a message here, not a commitment, and the inner proof's paths to the pads root are not modelled. Both are
     open item 2, which names them.

## The questions

**Q1 (overclaims, vacuity).** I found no overclaim.
* `inner_sound` (`Inner.lean:539-553`) is proved by cases on joint δ-agreement of `[Ch, Cμ]`.
  * Close case (`inner_close`, 447-504): the sacrifice ε, the batch γ and β cost 1/|F| each. Then any `y ≠ mh + β·mμ`
    agrees with `Ch + β·Cμ` on fewer than `s + nP + (N − |S|) ≤ (1−δ)N` positions (`step_beta_close`, 375-443), which
    gives `(1−δ)^q`.
  * Far case (`inner_far`, 509-534): BCIKS20 in the unique-decoding regime gives `N/|F|`, through ArkLib's
    `RS_correlatedAgreement_affineLines_uniqueDecodingRegime` (`prCoin_close_le`, 252-272). The queries then give
    `(1−δ)^q`.
  * The total is at most `(N+3)/|F| + (1−δ)^q`.
* `zk_compose` (`Compose.lean:57-102`): the pads `C` are received before the phase (`repZK`, 26-31). `InnerGood`'s
  pad vector is unique by `agree_unique` (35-53, from `2δN ≤ N − L`). So the phase's event is charged at one `h` with
  `h_ab = h_fa·h_fb`, which is exactly `hcouple`.
* `table_sound_pad_zk` and `tableAfterZK_sound` (`Table.lean:68-140`) are `table_sound_pad`'s proof with each rep's
  term raised by εInner (`rep_sound_pad_zk`, 46-63).
* `sessionZK_sound(_any)`, `zk_knowledgeSound` and the counts are as stated (`Session.lean:141-327`).
* The numbers check out: `(2^13)/2^128 + (9/16)^168 ≈ 2^-115 + 2^-139.4 ≤ 2^-114`, and
  `2·2^-205 + 2·2^-228 ≤ 2^-203` (`Numbers.lean:85-169`).
* For satisfiability at M1, see finding 2.

**Q2 (rows and inner proof against live, `final_c'` absorbed).**
* `restZK` receives `fc ← recv F` after level 0 and levels 1+, and before `innerGame`'s ε (`Algebraic.lean:368-371`,
  `Compose.lean:28-30`). The theorems therefore hold for a verifier that absorbs `final_c'` at any point before ε. The
  ruled fix (after `LABEL_INNER`, before ε) is one, and so is any earlier point, since a Lean strategy may pick `fc`
  from any prefix of the transcript.
* The rows match term by term against `PROTOCOL.md:135-148`, in characteristic 2:
  * zerocheck c_eval `Σ W_c(z)(r1c' + h) + fc' + h_fc` against `zc.vc + mskF fc`, where `zc.vc = Σ lagΛ z·mskF(r1c)`
    (`Algebraic.lean:179-191`, live `zk_veil.rs:669-670`);
  * a·b `G + a'b' + a'h_fb + b'h_fa + h_ab` (`Algebraic.lean:190`, live 693);
  * lincheck final `running + Σ comb·(zp' + h)` (`lincheckZK`, 274-287, live 743);
  * ring switch ab `claim_check + Σ λ(zp' + h)` against `ab.value + cF ca`;
  * ring switch c `claim_check + fc' + h_fc` against `mskF fc + cF cc` (live `flock-circuit.rs:440-441`);
  * the lane rows `claim_k + ρ_0 e_0 + ρ_1 e_1 + T'` in two limbs, with `claim_0 = target + β(y' + h)`
    (`Level0.lean:243-261`, `limbRows` 109);
  * the triple's three (`Inner.lean:66-70` against `PROTOCOL.md:145-147`).
* The γ count is `nA + 3 = 7 + 3 = 10`, which equals `cons.len()` (`zk_veil.rs:996`) and the "squeeze γ (10)" of
  `PROTOCOL.md:57`.
* The inner proof's order is ε, ρσ, γ, τ, β, Y, then the queries, the same in `innerGame` (`Inner.lean:112-121`) and
  live (`zk_veil.rs:985-1010`, `PROTOCOL.md:57-58`).
* The checks are the same.
  * Lean's `innerCheck` (96-101) checks `Σ c_i·head(y)_i = batchT + βτ`, where `batchT = −Σγ·const = +Σγ·const` in
    characteristic 2. Live checks `⟨c, Y[..s]⟩ = t + βτ`.
  * Lean checks `enc(y)(pos w_j) = Ch + β·Cμ` at `q` positions. Live checks `C(Y)_j = C_h[j] + βC_mu[j]` (§5 step 5).
* The order of the rows: see finding 3.

**Q3 (max, not sum).** The maximum is right.
* `ksAvgZK = avg_ω ⨆_j bound_j` (`Session.lean:277-279`) has the shape of main's `ksAvgB` (`Audit/FlockBatched.lean:142-144`).
* `KnowledgeSound` charges one target unit per draw (`Audit/Extraction.lean:69-71`, `atTgt` 31-32). So `ks` at the
  target's table, at most `sessionZK_sound`'s bound for that table, is at most the plan's maximum (`zk_knowledgeSound`,
  `Session.lean:282-289`).
* `zk_flock_count_execOS` is `Prog.flock_headline`'s curve (`Headline.lean:58-93`): `miss(K)` through
  `Law.execOS_miss_le` under A3, plus `ε_ks`, plus `δ_link`.
* Two things are absent, both open (items 2 and 4): `δ_tree` and `execAccept`.
* `δ_link` is a hypothesis over a generic committed transcript `Xc`. The headline instead uses `Xpub … Xplur` under
  `ecr/sha-512`, as `flock_batched_count` leaves it at M0 (`FlockBatched.lean:160-169`).

**Q4 (reused clear pieces).** Nothing is wrong.
* The coupling chain runs `zerocheckZK_couple` → `lincheckZK_couple` → `restZK_couple`, all against `Model.repPad`
  (`Model/LigeritoPad.lean:124-134`; `Algebraic.lean:444-453`).
* The product row and `InnerGood` use the same triple indices: `tr.fa`, `tr.fb`, `tr.ab` at `Algebraic.lean:190, 209`
  and `Inner.lean:128`.
* `openingZK` runs `opStep` once per claim and `opResult` on claims whose values are their own claim checks
  (`Algebraic.lean:321-331`). This is the live `values = [cc_ab, cc_c, extras]` (`flock-circuit.rs:443`).
* `opResult_two` (336-354) shows that this is the clear `opResult` when the checks equal the unmasked values. Rows 0,
  1 and 2 force `ca = ab.value(h)` and `cc = zc.vc(h)` (`restZK_couple`, 416-422), so a late `fc` gains nothing in the
  clear game.
* `CommittedPad` and `padWits` are unchanged (`SoundnessPad.lean:30-38`): the target is `C₀`'s witness lanes. The
  rep's extra lanes `2^k0 + e·r + i` (`Model/LigeritoPad.lean:86`) are live's `64 + 2r + i`.
* `rep_sound_pad` and `link_sound_pad` are applied with the same `e` as `Pads0 np e` (`Table.lean:61-63, 98-104`).
* `lean-audit.json` has only additions. Some module digests changed because new read-definitions were recorded; every
  existing hash is unchanged (e.g. `Model.padCorr`, `Game.send`).
* The `Arklib` dependency digest changed because of the new import
  `ArkLib.Data.CodingTheory.ProximityGap.BCIKS20.AffineLines.UniqueDecoding` (`Inner.lean:4`, which nothing on main
  imports). `lake-manifest.json` is unchanged, so this is not a bump.

**Q5 (open guarantees).** The six items are right, but the M1 scope is missing (finding 1).
* The refinement differences in finding 3 belong under item 4.
* Item 2 already names τ, the pads and the inner proof's openings.

## No build needed

No finding rests on a hypothesis that needs a build.
