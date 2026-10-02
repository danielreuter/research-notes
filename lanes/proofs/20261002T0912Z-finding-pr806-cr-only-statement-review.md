---
id: proofs/20261002T0912Z-finding-pr806-cr-only-statement-review
campaign: e2e-guarantees
lane: proofs
kind: finding
status: final
repo: danielreuter/verity
origin: cursor/zk-lean-cr-only-95d4@0162b6d64
---

# Statement review: #806, soundness under `cr/sha-512` alone and hm96 hiding proved (29 new pins), APPROVE

Reviewer: proofs (bc-8416bc72), 2:12 AM PDT Oct 2. Head `0162b6d64` (`cursor/zk-lean-cr-only-95d4`), merge base
`b8c9dd478`. I read the review text `art:bd1b0842…` (each new signature and each definition it reads) and the source.

## What I compared

- `lean-audit.json` at the head against the merge base: 214 pins become 243. None is removed or changed. 77 read groups
  change only in their `pins` lists, and two are new (`CROnly.Defs`, `CROnly.Hm96Defs`). The top-level `roots`,
  `assumptions`, `upstream` and `dependencies` are unchanged.
- The 15 restated end-to-end theorems against their originals, token by token, binders and bound:
  `Partition.flock_e2e_{count,drawn}`, `_exec`, `_hm96`, `_exec_hm96`, `Prog.flock_e2e_{count,drawn}`,
  `Prog.flock_headline` and the four `UProg.flock_e2e_*_classes(_zero)`. Each differs in the same five places and
  nowhere else (apart from names written in full, such as `Binding.Layout` and `Audit.Partition.tabOf`):
  1. a new budget `q` with `hq : 0 < q`;
  2. `ht : 0 ≤ t'` becomes `0 < t'`;
  3. `hCR : LinkCR … t'` becomes `hCRs : LinkCRStrict … t' q`;
  4. the bound's `linkBoundE … t'` becomes `linkBoundE … (strictRunCost t' q)`;
  5. the name.
- `session_shvzk_le`/`_gap` against `Session.session_shvzk_hm96`, and `adaptive_prefinal_le`/`_gap` against
  `Session.adaptive_prefinal_hm96_tape`. The only change is `hT1 : Hm96Hiding My cs δ₁` becoming `hδ : hidingGap My cs ≤ δ`
  (or nothing, at δ = the gap). `session_shvzk_*` also asks that every table share one `(My, cs)` (`hMy`, `hcs`).

## The definitions

- `truncOut`/`truncCost`: the finder stopped at `q` evaluations, which outputs nothing where it would make more. It
  makes at most `q` on every outcome, and its collisions are a subset of the finder's.
- `LinkCRStrict`: `Assumptions.SHA512CRStrict` (unchanged from main: `q²/2^513` for a finder capped at `q` on every
  outcome) for exactly the finders `LinkCR` builds, stopped at `q`. Like `LinkCR`, it is a predicate on the finders
  built from this prover, not on every finder.
- `strictRunCost t' q = 2^256·(t'/q + q²/2^513)`. `linkCR_of_strict` and `expected_of_strict` (Markov on the cost)
  carry it to `LinkCR`.
- `hidingGap`: the statistical distance of `(My y, c y)` from `(U, c y)`, summed over `B × c(Y)`, which holds both
  supports. `Universal`: the standard universal family. `hankel`: `(M(κ)y)_i = Σ_j κ_{i+j} y_j`.
- `sum_hidingGap_le` is the leftover hash lemma with side information. It gives `hm96_sha512_sum` (a mean gap of at most
  `2^-257` over uniform keys) and `hm96_sha512_bad_keys` (at most `2^-64` of the keys fail `2^-193`).

## Result

`CROnly.flock_headline`'s cryptographic hypotheses are all instances of `SHA512CRStrict`: `hCRs`, plus `hKS` and
`hT`, which are unchanged from main and already strict. A3 (`hA3`) is beside them. Nothing in the e2e statements
reads `SHA512CRExpected` any more.

## Scope (not defects)

1. `0 < t'` excludes only a prover that costs nothing.
2. The derived link term `2(1 + k)(t'/q + q²/2^513)` is looser than the direct `q²/2^513 + 2(1 + k)t'/q`, by
   `2(1 + k)` on the `q²` term. At the best `q` it is `3(1 + k)·q²/2^512` (`linkBoundE_at_cube`). That is the price of
   `cr/sha-512` alone. With k = 1 and before the `Q_s/(1 − ρ)` factor, `t' = 2^100` gives `q = 2^204` and a hash part of
   `6·2^-104 ≈ 2^-101` (under `ecr/sha-512` it was `2^-154`). `2^-128` holds up to about `t' = 2^60` evaluations a run.
3. The ZK forms with a key (`adaptive_prefinal_key`, `_hm96_sha512`) draw the key uniformly inside the probability,
   and the verifier and distinguisher see it. The protocol pins a hash-derived key today, so "the pinned key is
   uniform" stays a model fact (ZK.lean's docstring says so). That is A6's open protocol decision. It concerns ZK only.
