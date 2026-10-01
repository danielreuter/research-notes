---
id: 20261001T2040Z-handoff-from-proofs-ir-qcall-attention-133-not-72
campaign: verity
lane: proofs
kind: handoff
status: open
repo: verity
origin: proofs-ir (bc-6cd83494)
---

# `Q_call` v1 cuts the attention block into 133 units, not about 72

to: proofs (bc-8416bc72). From proofs-ir. No standard program is refused. The counts are right for the agreed model, but one of
them is not what the brief expected.

needs-proofs: do you want a merge rule in `Q_call`? I recommend not in v1; land it as agreed, and take the rule to Daniel if 133
units matters to him.
- Under `Q_call` the Boolean attention block `AttnBlock_v8{D=16,NVIS=16,FIRST=False,…}` is 133 units and 3,983 bits. The word block
  `AttnBlock_v5` is 133 units under `Q_call` too: the two cut identically.
- The word Program's 72 is `Q_word` v1's count. `Q_word` merges a gate into its only consumer's unit, and `Q_call` has no merge
  step: a Call that doesn't fit is cut into its 120 body nodes, and each node that fits is one unit.
- Getting near 72 would need a rule such as "merge a node into its only reader while the result still fits X". That would be a
  `Q_call` v2, on Daniel's go.

The full table and explanation are in `note:proofs/20261001T2034Z-draft-from-proofs-ir-qcall-pr-body-213f4361b`, under "The
attention block against the word Program's 72".
