---
id: proofs/20261002T0939Z-finding-pr801-hedge-merge-statement-review
campaign: e2e-guarantees
lane: proofs
kind: finding
status: final
repo: danielreuter/verity
origin: cursor/e2e-const-95d4@cf7641033
---

# Statement review: #801 after merging the hedge `b0bae1b87`, APPROVE at `cf7641033`

Reviewer: proofs (bc-8416bc72), 2:39 AM PDT Oct 2. It follows
`note:proofs/20261002T0838Z-finding-e2e-pp-statement-review` (APPROVE at `f5a7d2b12`). e2e-placed merged the hedge in
three commits: `0846d7b11` (the merge), `5ddab8028` (#801's definitions following #776's Δ) and `cf7641033`
(`lean-audit.json` from `--update`). I read its `--update` output (in `internal/proofs/e2e/e2e-placed.md`, "#801 hedge
merge").

## Pins

`lean-audit.json` at `cf7641033` holds 270 pins: 214 base, #801's 49 and the hedge's 7. Every #801 pin's record equals
the one at `f5a7d2b12`, and every other pin's equals the one at `b0bae1b87`. None is missing, none extra, and the
top-level fields equal the hedge's. No theorem statement changed.

## Changed definitions the pins read

- **#801's own, changed by `5ddab8028`:**
  - `Discharge.Aliased.srcAt` now follows #776's `Flat.leafSrc` / `Flat.cutSrc` case by case. A leaf port gives `.zero`
    for a negative leaf, or for a bit with `16·(x − start) + t` past its row's `bits`; otherwise it gives the same
    `.msg q byte bit` as `msgCol`'s arguments. A cut port, at the first matching cut, gives `.msg` only when `t < 16` and
    the bit is within the row's `bits`. The wire and literal cases are unchanged.
  - `Discharge.Zero.ZeroPort` lists exactly `srcAt`'s `.zero` cases (both leaf forms, and the first-cut form), so
    `srcAt_zero_iff` reads as before.
  - Both now describe what the executable's Δ does after #776: bits past a row's length copy the forced-zero row. That
    makes them right, not weaker. `flatSrc_key` and `flatSrc_zero` tie them to the hedge's `leafSrc` / `cutSrc`, with
    statements unchanged.
- **The hedge's, now read by #801's pins:** `ParseFacts` (without `ports`), `Flat.RowBit` (`ShaRowBit ∨ HmRowBit`),
  `Flat.cutSrc`, `Flat.leafSrc`, `Typed.msgCol` (the hm96 slot's pad past the chain), and the new `ShaRowBit` and
  `HmRowBit`. These are #776's content, reviewed in #776. #801 only reads them.

The scope points of the 0838Z review stand unchanged.
