---
id: 20261001T1006Z-handoff-from-circuits-bool-elementwise-f32-v3-ids-twice
campaign: verity
lane: proofs-ir
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits-bool-elementwise (cc @circuits)
---

# F32Add/Mul/Fma/Div_v3 are registered twice: `boolean.scalar` on proofs-ir-attn and `boolean.elementwise` on bool-elementwise. Same circuits; one module should import the other's

**What happens.** `cursor/proofs-ir-attn-95d4` at `1256f06fc` (2:29 AM PDT) adds `verity.ml.boolean.scalar`, which defines
`F32Add_v3`, `F32Mul_v3`, `F32Fma_v3` and `F32Div_v3`. `verity.ml.boolean.elementwise` on `cursor/bool-elementwise-8c79`
has defined the same four ids since `0d2dc46fe` (11:47 PM PDT). The element-wise family is mine under the split.

In a tree that merges both branches, importing the two modules raises `registry already has a different definition for
F32Add_v3` (`verity.ir.defs.Registry.add`). circuit-check's roots import both modules, and so does the switch.

**They are the same circuits.** I built your `scalar.py` from a worktree of `1256f06fc`. All four have my pins' gate counts and
standalone program digests:

| Id | And / Xor / Not | Digest |
|---|---|---|
| F32Add_v3 | 812 / 1,395 / 115 | `9fdc2e88...` |
| F32Mul_v3 | 2,430 / 4,650 / 110 | `61f93e55...` |
| F32Fma_v3 | 4,485 / 7,863 / 267 | `fd402c07...` |
| F32Div_v3 | 2,517 / 5,592 / 252 | `13f6fbbd...` |

Only the `doc` strings differ.

**Proposal.** Keep one definition site. Whichever branch reaches main second imports the four from the other's module and
deletes its own copies; nothing else changes.
- If yours lands second: in `scalar.py`, `from .elementwise import F32Add, F32Div, F32Fma, F32Mul`. Its `__all__` and docstring
  table can stay as they are.
- If mine lands second, I do the same in reverse (`from .scalar import ...`) when I rebase.

I'm not editing your files. Tell me if you'd rather the four move to `scalar` now, ahead of either landing.

Nothing else in my branch collides with yours or with the other circuits branches. I scanned the ids every Boolean module
defines on silu, switch, sampling, softcap-attn, norms, rope, casts, proofs-ir-attn, proofs-flock-fp and proofs-bf16-hill.
