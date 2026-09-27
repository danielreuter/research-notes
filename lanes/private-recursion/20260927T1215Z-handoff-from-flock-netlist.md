---
id: private-recursion/20260927T1215Z-handoff-from-flock-netlist
campaign: verity
lane: private-recursion
kind: handoff
status: open
repo: danielreuter/verity
origin: PR #83 @ 92f3ba6d
cursor:
  subagentId: "bc-ff572e70-b0e7-5094-85be-13ff9ddc4d6a"
---

# The glue prover is now one pass over the witness: 0.18 s -> 0.002 s on the demo (92f3ba6d)

Follows `note:private-recursion/20260927T1150Z-handoff-from-flock-netlist`.

**The dense prover can't scale.** The late rounds need `z` folded over sibling blocks outside the glued regions, so the prover
is one pass over the committed witness at minimum.

**The prover now matches that bound:**
- the 7 rounds inside a word read only the words `W` touches;
- every word then folds once to the seven coins, giving `2^(M-7)` field elements (about 1 GB at M = 33);
- the remaining rounds are dense over those, with `W` sparse throughout.

Its messages equal the dense prover's (tested on an honest and a broken witness).

**Demo again (SHA-512 → GF(2^128), M = 22):**
- 2 relations: prove 0.71 s, glue prove 0.002 s;
- 256 relations: prove 0.71 s, glue prove 0.002 s, glue verify 0.24 ms.

**At V[B]'s M = 31–35,** the glue prover's cost is that one fold, about `2^M` bit-weight additions, which is the order of a
zerocheck pass.
