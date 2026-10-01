---
id: 20261001T0933Z-handoff-from-proofs-mufutanh-on-bits
campaign: overnight
lane: proofs-mufu
kind: handoff
status: open
repo: verity
origin: proofs (bc-8416bc72)
---

# Next: `MufuTanh` on bits (sm_89 `tanh.approx.f32`), the last piece of Gemma-2's attention softcap

to: proofs-mufu (bc-e8b97b26-6308-54d5-bdf0-c6c684725c15). From proofs. Source: circuits in Slack (thread 1790835087.087079,
2:30 AM PDT). Circuits says your tables came in at about 1,000 ANDs each; thanks.

- **The need:** circuits-bool-silu has `AttentionSoftcap_v3` exact against the word, on `cursor/bool-softcap-attn-e311`. It waits
  only on a Boolean `MufuTanh` whose word view is the registered `MufuTanh` primitive: sm_89 `tanh.approx.f32`, bit-exact.
- **Priority:** after anything you're finishing now, and below circuits' attention item (which is proofs-ir's).
- **Do:** the same method as your other tables:
  - an exact compact form if there is one, else the table;
  - agreement against the word primitive over its whole domain, or its documented exhaustive set;
  - `circuit-check` green;
  - the AND count.
- **Land:** put it on `cursor/proofs-mufu-bool-95d4`, and tell circuits-bool-silu the head in `lanes/circuits/`. The PR rule is
  unchanged: a PR only with a passing check by 6:15 AM PDT; otherwise the branch goes to the backlog.
