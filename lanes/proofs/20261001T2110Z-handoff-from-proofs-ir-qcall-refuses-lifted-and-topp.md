---
id: 20261001T2110Z-handoff-from-proofs-ir-qcall-refuses-lifted-and-topp
campaign: verity
lane: proofs
kind: handoff
status: open
repo: verity
origin: proofs-ir (bc-6cd83494)
---

# `Q_call` v1 refuses the lifted serving program and the top-p sampler (gate wider than 32 bits)

to: proofs (bc-8416bc72). From proofs-ir. The check `r20261001-203205-c3c1` on `213f4361b` passed. Its circuit-check summary
reads "97 Definition(s) Q_call v1 refuses", all for `gate-too-wide`, as warnings on 48 targets. That is the agreed rule ("a
primitive gate whose own output exceeds X bits makes the query inapplicable"), but the refused programs include standard ones.

needs-proofs: which remedy should a lifted program get? My recommendation is to land Q_call v1 as it is. Then, if lifted
programs need Q_call, take Daniel one of three:
- **(a)** `X = 33` for lifted programs. This is one parameter, and the reference already takes any X; a unit's outputs are then
  one lifted word.
- **(b)** Represent the ⊥ tag as its own 1-bit gate. This is new lifted Definition ids, a vllm change.
- **(c)** Allow wide gates in a `Q_call` v2.

For the top-p word, the natural fix is the program's: lower `TopPMaskWordx{V}` to 32-bit pieces or bits, new ids. Nothing in
this PR changes the rule.

The two families:
1. **Every lifted Definition:** `Lifted[…]_v2` (every arithmetic, constant, dot, GEMM, attention and RMSNorm lift), `LSelect32_v1`,
   and the programs built on them.
   - Those programs include **`LServe_v2`** (the lifted padded serving Program), `LMoeBlock_v1`, `LMoeBlockL_v1`, `LMoeFfn_v1`
     and `LMoeFfnL_v1`.
   - Cause: a lifted w-bit domain is w+1 bits, with the ⊥ tag in bit w (LIFTING-SPEC A3,
     `verity_vllm/program/registry/lifted.py`). So every lifted 32-bit word is a 33-bit gate.
2. **`TopPMaskWordx64_v1`**, the 64-bit top-p keep word (one bit per vocabulary token), and its callers `TopPMask_v1{V=64}` and
   `GumbelTopPTokenSelect_v1{V=64}`.

None of the brief's Calls is refused. The table is in `note:proofs/20261001T2034Z-draft-from-proofs-ir-qcall-pr-body-213f4361b`,
which now lists these refusals.
