---
id: proofs/20261002T0959Z-finding-word-bits-statement-review
campaign: e2e-guarantees
lane: proofs
kind: finding
status: open
repo: verity
origin: proofs bc-8416bc72
---

# `word_bits` (`cursor/registered-word-bits-95d4` @ `717c813b1`): statement review APPROVE

Reviewer @proofs read both `audit.py --update` outputs (`internal/proofs/word-bits-lean-records.md`): the verifier
package (PASS with replay, 4890 declarations, 17 pins) and FlockSoundness (PASS without replay, 212 pins).

- **One pinned statement changed, and it says more.** `Flock.Registered.check_ok`'s conclusion gains one conjunct,
  `reg.fits c.ports[p]!.words = true`, between the port-name equality and the per-instance openings. Every other
  conjunct is token-identical before and after.
- **Definitions read.**
  - `Port` gains `words : Option Nat` and `wordBits : Nat`; `Port.domain` and `Port.reads` move only as projections.
  - `rowWords w b = ⌈w·(b/16)/64⌉·64` is the statement's padded u16 row (whole SHA-512 blocks, each leaf `b/16` words).
  - `Port.fits reg n = reg.words.all (n == rowWords · reg.wordBits)`.
  - `checkPort` refuses a port that doesn't fit, after finding the port and before any opening.
  - `opensLeaf_binding`'s statement is unchanged.
- **FlockSoundness.** Only the records of `Flock.Registered.Port` and `Port.domain` move (two new fields). No soundness
  pin's statement changes, and none reads `fits`.
- **Caveat, non-blocking.** `fits` is vacuously true when `words = none`. `ofJson` allows that only for a 16-bit file
  that names neither key (set 16's pinned reads files), where the rows are the port's own. `check_ok` quantifies over the
  verifier's own `own : Array Port`, not over what `ofJson` can produce. So for such files the new conjunct adds nothing,
  and the width check has content only for files that name `words`, which `reads_file` now always writes.
- **After a main merge:** the textual merge of both packages' `lean-audit.json` with main `9699b2f28` is the per-key
  union, with no record changed on both sides (checked against `d9f804670`). A head that only merges main keeps this
  review; I re-label at it.

PR [#811](https://github.com/danielreuter/verity/pull/811). Grant `statement-reviewer` at `pr:811@717c813b1`.
