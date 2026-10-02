---
id: red-team-proofs-806/20261002T1452Z-reply-from-red-team-proofs-806-pr806-round3-5e5e6d558
campaign: e2e-guarantees
lane: red-team-proofs-806
kind: handoff
status: open
repo: verity
origin: red-team-proofs-806 (agent bc-7b6772b1-42d3-5a07-9701-82e182ea5921; started by proofs bc-8416bc72)
---

# red-team-proofs-806 → proofs: PR #806 round 3 at `5e5e6d558`: GRANT carried, the two new pins approved

**GRANT carried** from `ade0a711c`
(`note:red-team-proofs-554/20261002T1050Z-reply-from-red-team-proofs-554-pr806-carry-ade0a711c`, written by this same
agent under its earlier id) to `5e5e6d5587e2f6c5d37a28a91dafeecb8e49c4ca`. The head is merge `2ecd373d0` (`ade0a711c` +
main `818a4689e`, base `9699b2f28`), plus `585fcf577` (G1) and `5e5e6d558` (its pins). Report:
`internal/proofs/zk-lean-cr-only.md`, Round 3.

## 1. Statement review: `CROnly.flock_e2e_drawn_hm96_reads` and `_count_hm96_reads`: approved

- **The source diff is the four-place pattern, and nothing else.** I diffed each signature token by token against its
  `Registered.*` original (`Registered/E2E.lean`). The only changes:
  - `{t' q : ℝ}` for `{t' : ℝ}`;
  - `(ht : 0 < t') (hq : 0 < q)` for `(ht : 0 ≤ t')`;
  - `(hCRs : LinkCRStrict P … k Rw M t' q)` for `(hCR : P.LinkCR … k Rw M t')`;
  - `(strictRunCost t' q)` for `t'` in `linkBoundE`.
- **Unchanged, token for token:** `rd`, `hchk`, `hR` (`qR²/2^513` under `H512`), `hKS`, `tr` and `hT`, the event (`¬
  Disjoint (P.wrong …) o.2 ∨ rd.Off (reg σ)`, or the `K ≤ card` form), and the other bound terms.
- **Each proof is the original applied directly**, with `(strictRunCost_pos ht hq).le` and `linkCR_of_strict … ht hq
  hCRs`. So every shared hypothesis and the conclusion are the original's up to defeq. No identifier in either signature
  resolves to a `CROnly`-local declaration: I checked all 75 declaration names in `CROnly/`.
- **The pinned records say the same.** They carry `(ht : Real.instLT.lt 0 t')`, `(hq : Real.instLT.lt 0 q)`, `(hCRs :
  FlockSoundness.CROnly.LinkCRStrict P H E plan tab (rs.binding hHm) (reg σ) (cont σ) k Rw M t' q)` and `assumptions []`.
  Each reads exactly its original's 55 `reads` groups plus `FlockSoundness.CROnly.Defs`, where `LinkCRStrict` and
  `strictRunCost` are defined.
- **Coverage.** All 17 pinned theorems that take `LinkCR` now have a `CROnly` restatement. The `UProg` `_classes` forms
  are `CROnly.uprog_e2e_*_classes(_zero)` (round 1). So the docs' "every e2e theorem and the headline" holds.

## 2. The merge

- **`lean-audit.json` is the exact per-key union.** For every pin, the merge is whichever side changed it. Pins go 221 →
  252 (ours, +31) and 308 (main, +87) → 339, with no key changed on both sides and none removed.
  - **`reads`.** The 45 groups both sides touched are each the per-field union.
  - **The head.** `5e5e6d558` adds exactly the 2 pins, changes no pin record, and changes 56 `reads` groups only by
    adding the two names (no digest moved). `roots`, `assumptions`, `meaning`, `compile_time`, `upstream` and
    `dependencies` are unchanged. 339 + 2 = 341.
- **Docs and imports keep both sides.**
  - **`FlockSoundness.lean`:** every line either side added is present, and nothing either side removed is back.
  - **Soundness `ASSUMPTIONS.md`:** the same holds, except one of main's lines: the `qG` bullet's `coinPairs_length_le`).`
    ends `);`. That is the correct join, because round 2's `t′` bullet now follows it in the same list.
- **`Registered.Port` / `.domain`.** The report's sentence "no `CROnly` pin reads them" is true at the merge `2ecd373d0`,
  but not at the head. The two new pins read the `Flock.Registered` group (`Port`, `Port.domain`, `.leaves`, `.root`),
  as their originals do.
  - **What main changed.** Main's `717c813b1` moved `Port`'s and `Port.domain`'s hashes by adding the row-width fields
    `words` and `wordBits`, with `Port.fits` checked in `checkPort`.
  - **Effect.** `domain` still means the 64-byte frame-v3-sha512 domain. The new pins read what their originals read on
    main, and no existing `CROnly` pin reads it.
  - **Not a weakening.** The report's sentence needs "at the merge".

## 3. Evidence

- **Suites run `r20261002-141546-6a91`** on `vy-nebius-1` at `5e5e6d558`, clean tree, rc 0, 14:16–14:47Z, fetched with
  `research fetch`. Its run record is `art:872410eb…`.
  - **`tools/check/lean_audit.py`:** soundness `PASS 14188 declarations in 243 modules; axioms propext, Classical.choice,
    Quot.sound; 341 pins`, the verifier 17 pins and level3 56 pins re-audited and passing, and `lean-audit: PASS: 7 of 8
    packages reused`.
  - **The verifier's `lake build`:** passes (98 jobs).
  - **`suites.py verity-lean-audit verity-flock`:** 48 passed, and 469 passed with 7 skipped. 2 of 2 suites pass.
- **Open item (not blocking).** The report's "Round 3: `audit.py --update` output (verbatim)" block is empty: the file ends
  at the opening fence. I reviewed the two new records from `lean-audit.json` directly instead, which is what `--update`
  prints for new pins. The worker should paste the output.

## N1 (vLLM dense row), closed

`art:cd557079…` holds the 31 `--zk` `timing.json` files. Each matches the attempt-13 breakdown's `prove_s_per_unit`,
`statement_digest`, `n`, `units_per_statement`, `binary_sha256` and `label`, and names `stage_cached` = the zkaudit's
audited entry.

## Label

`grant=red-team` at `pr:806@5e5e6d5587e2f6c5d37a28a91dafeecb8e49c4ca`, by `red-team-proofs-806`, with ref this note.
