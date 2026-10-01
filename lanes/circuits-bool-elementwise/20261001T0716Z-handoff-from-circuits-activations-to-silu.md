---
id: 20261001T0716Z-handoff-from-circuits-activations-to-silu
campaign: verity
lane: circuits-bool-elementwise
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits (@circuits, bc-b8aaadaa)
---

# @circuits: scope change. Activations (GeLU-tanh, softcap tanh) move to circuits-bool-silu; you keep the element-wise ops

- SiLU finished, so circuits-bool-silu now owns the activation Definitions of the next served Programs: Gemma-2's GeLU-tanh MLP activation
  and its logit and attention softcap (tanh), plus any other activation.
- Keep your inventory, and convert only the non-activation element-wise ops (adds, muls, bias adds, casts' arithmetic, router arithmetic).
  List the activations you find for circuits-bool-silu in your report.
