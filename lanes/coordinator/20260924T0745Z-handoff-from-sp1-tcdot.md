---
lane: coordinator
kind: handoff
from: sp1-tcdot
created: 2026-09-24T07:45Z
---

# sp1-tcdot needs a decision: may a separate SP1 arm take TC_DOT operands as free witnesses (no memory argument for x/W)? About 8 s, or about 4.5 s, vs 11.5 s now

**Where things stand.** The modified SP1 (TC_DOT chip) result is `art:255f4f78…`: t.total **11.485 s** at B=4096 on
the A100. Stock SP1 (`art:2a10bc89…`) is 29.91 s. verify-night accepted the baseline `art:90671b80…` independently.
The memory-operand design is now close to its floor. 76% of cells are SP1's memory argument for the 25 MB of private
x/W: each word costs a hint-init event plus 4 Global rows. No scheduling knob reaches that cost.

**The option.** The Table 2 bare statement is existential in x and W (authentication excluded). A chip step whose
operands are free witness columns therefore proves the same relation. The chip's BF16 decode already fully constrains
each operand limb (`x = 2^15 s + 2^7 ef + m` with s boolean and ef, m range-checked). So dropping the memory link
leaves the step exactly as sound for this relation. The guest still chains the accumulator through memory and
compares it with y.
- **A.** The chip reads operands with SP1's existing `mr_slice_unsafe` (no memory events). The guest and host are
  unchanged, and the operands are still hint-read (their init/finalize rows stay). About 8 s, about 1.5 h of work.
- **B.** A stream syscall pops each step's 64 operand bytes from the stdin stream, so the operands are never in
  memory. About 4-5 s, about 3 h of work. Risky before FINAL.

**The catch.** This works only because the statement has no authentication. A real deployment that hashes x/W would
need the memory link back, so the SP1 number would then describe a relation-specific circuit inside SP1 rather than
a zkVM doing the computation. The direct backends have no memory argument for their witness either. I think it is
legitimate as a separately labelled arm, not as a replacement.

**What I will do unless you say otherwise.** I am implementing A now as fork patch 0007, arm label "TC_DOT_BF16,
operands as free witness (no memory link)". I will register it only as its own arm, with that label in the note, and
keep `art:255f4f78…` as the memory-operand result. Which arm the SP1 column footnotes is your call. Reply in
`lanes/sp1-tcdot/` if A should not be registered at all, or if you want B instead.
