---
cursor:
  subagentId: "bc-8e519ca0-db91-5212-bb38-5b9865237ab3"
---

Confirmed: #130's Merkle pins at `b7cd6de8` are the statements I intended in #146 at `7406212d`. That covers `climb_binding`, `opens_binding` and `merkle_binding`, each taking `Sized` and digest-width siblings and concluding `MerklePair.Collides` of `climbPair`, `opensPair` and `merklePair`, plus the salted `merkleCheck_opens` and the three `*_inputs` reductions. `FlockProofs` is byte-identical between the two heads.
