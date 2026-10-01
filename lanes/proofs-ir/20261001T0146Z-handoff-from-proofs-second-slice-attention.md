---
id: 20261001T0146Z-handoff-from-proofs-second-slice-attention
campaign: verity
lane: proofs-ir
kind: handoff
status: open
repo: danielreuter/verity
origin: proofs (bc-8416bc72)
---

# Second Boolean IR slice, picked by circuits: `AttentionHead_v3` / `Attention_v3` (FA2 on sm_120), queued after the BF16 coordinate

to: proofs-ir (bc-6cd83494). The top-level ruled at 6:41 PM PDT that circuits picks the second slice. Circuits'
pick, verified as @circuits, is in Slack thread `1790818944.596569`.

- **What:** a Boolean `AttentionHead_v3` / `Attention_v3` for FA2 on sm_120 (RTX PRO 6000).
- **Why circuits picked it:**
  - it's in every deployment;
  - it carries the largest share of word-check cost;
  - the narrowest-cut partition folds it first, taking scores and probabilities into a head's output words.
- **Order:** start it after `GemmCoordinate_v3` (BF16) is circuit-check green and proved by C-Flock. Don't interleave the two.
- **Inputs:**
  - the existing word-level attention Definitions in `verity.ml` and circuits' FA2 sm_120 binding;
  - Daniel's rulings (`note:20261001T0125Z-handoff-from-proofs-daniel-rulings`). The special-function tables are
    already Boolean (one-hot ROM), and XOR and AND take any number of inputs, so softmax's `ex2` and `rcp` tables become
    ROM Definitions. Conformance is out of scope: the circuit only has to explain the I/O vLLM serves.
- **Interface with circuits:** circuits sends questions about the FA2 binding, tiling or which head shapes come first
  to `lanes/proofs/`, and I route them. Your design questions come to me, as before.
- **GPUs are scarce** (Daniel, 6:35 PM PDT). This slice is CPU work, plus circuit-check. Any GPU proving goes through the
  proofs floor of two GPUs on node 1, held only while proving.

Checkpoint one line when the BF16 slice is done and the attention slice has started.
