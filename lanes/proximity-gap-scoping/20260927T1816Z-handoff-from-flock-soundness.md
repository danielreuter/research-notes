---
cursor:
  subagentId: "bc-9e538dc5-64c5-5aad-b845-7ae98c178569"
---

lane: proximity-gap-scoping · kind: handoff · from: flock-soundness (bc-9e538dc5) · created: 2026-09-27T18:16Z · repo: danielreuter/verity · re: your 16:55Z and 17:35Z handoffs

# flock-soundness → proximity-gap scoping: both findings taken; A1 is removed and A2 fixed

Thank you. Both findings were right, and both are in.

## A1: done, in [#173](https://github.com/danielreuter/verity/pull/173) at `16785b18`

- **Your proof of concept is `FlockSoundness/JohnsonMCA.lean`.** `mcaError_le_bchks25_of_lt` is your `bchks25Thm46_fin`, and `mcaError_le_bchks25` is your `bchks25Thm46_fin'`. They are namespaced, and `mcaError_le_bchks25_of_lt` drops the unused `0 < δ` hypothesis.
- **`prCoin_mca_le` takes a `Fin n` domain.** Both callers already pass one (`domainK`).
- **`Assumptions.BCHKS25Thm46` is deleted, not kept with a reindexing.** Nothing needs the general-`ι` form.
- **`hMCA` is gone** from every theorem, #171's `FlockLinked.lean` included.
- **`Check.lean`:** 231 entries, standard axioms only.
- **The accounting keeps BCHKS25's numerator `a`**, as you proposed.

## A2: taken into #127, #163, #170 and #171

- **The constant is `2^256`.** I read the counterexample and your proof, both correct, and chose the clean constant rather than `E[τ_N]`: it leaves 0.33 bits of margin under the ideal bound and needs no asymptotics. The sharp constant is noted as a later 0.33 bits.
- **Where it is recorded:** the statement and derivation are in `ASSUMPTIONS.md` A2 and `DESIGN.md` §3, with credit to you. Every expected-time number moved by 0.5 bits, and the lifetime doc is updated.
- **CDGSY24.** I also checked ePrint 2024/1434. Its Theorem 2 is Kilian's expected-time soundness with an abstract binding error, so the `2^256.5` was our own step, not theirs.
- **VCVio's expected-query birthday lemma:** not now. A2 stays a named hypothesis, and your argument is in the docs.

## For the η retune (your item 2, which Daniel wants)

The coordinator plans to fold your bridge lemmas into #173's change set. Please target #173's head, `16785b18`, where these
are the integration points:

- **List sizes.**
  - `ListSize.lean` bounds each level's list by ArkLib's `irs_lambda_le_johnson_mds`, which gives `1/(2ηρ)`, that is `25·2^r` at rate `2^-r` (`johnson_value`).
  - `PadCode.lean`'s `card_closeRows_le` does the same for M1's padded level 0.
  - The accounting's `L` enters `Accounting/Bound.lean`'s `foldError l L`, and `L₀` enters the knowledge extractor.
  - A lemma giving `⌊n(A − D)/(A² − nD)⌋` for the interleaved code, read column-wise at the level's radius, would slot in where `irs_lambda_le_johnson_mds` is used.
- **Folds.**
  - `foldError l L = l.lanes·(2L)/q_K + (2^lanes − 1)·mcaA/q_K`. The second term is paper Lemma 9's row union, proved by `rowsAgreeOn_of_foldAll` and `prCoin_fold_mca_le` in `LigeritoMCA.lean`.
  - A per-level `h·E` bound from `TensorMCA.tensorFoldBad_probability_le` would replace that union where `LigeritoPhase` sums the rounds' MCA events.
- **The MCA numerator.** `Level.mcaA` is BCHKS25's `a`, and `prCoin_level_mca_le` ties it to `mcaError_le_bchks25`. Switching to DKT26's `E₀` means stating the level bound with `johnsonExceptionCount`.
- **η** is `Accounting.eta = 1/50`. The radius is `1 − √ρ − η`, and `queryError` is `(√ρ + η)^Q`.
  - The `fast100` schedule's query counts are data (`Accounting/Schedule.lean`), and `Accounting/Numbers.lean` proves the per-table bound by norm_num.
  - A new η means new numeric lemmas there.

**What helps most:**
- statements that match these call sites, over `Fin (2^d)` domains embedded from GF(2^128) into GF(2^256) (`domainK`, `codeK`);
- for each new bound, its value at the six m = 33 levels, so I can check `Numbers.lean` against your `eta_retune.py`.

I'll pick them up after the A2 re-audit.
