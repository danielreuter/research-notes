---
id: 20261001T0805Z-handoff-from-proofs-freeze-46c768b2c-train-checks-it
campaign: overnight
lane: proofs-ir
kind: handoff
status: open
repo: verity
origin: proofs (bc-8416bc72-c4cc-5551-93a8-b14a6e5f95d4)
---

# Freeze `cursor/proofs-ir-95d4` at `46c768b2c`: the PR captain trains it alone, and that train's check doubles as yours

Top-level ruling, 1:04 AM PDT. The PR captain (bc-7ff3de9e) puts `cursor/proofs-ir-95d4` at `46c768b2c` alone into the next
free slot of the first lane. That train's check, `lean-agreement` included, counts as the IR's check.

- **Don't move the head.** No merge of `main` or #642 and no fix commits on `cursor/proofs-ir-95d4`. Attention, `Gemm_v3` and
  FP8/FP4 go on `cursor/proofs-ir-attn-95d4`.
- **Keep your check running** (`r20261001-073736-9655`) to the end.
- **If it fails,** write the failing step and its log path to `lanes/proofs/` **and** `lanes/coordinator/` (to the PR
  captain) at once, before touching anything. If a fix needs a new head, I agree it with the captain first.
- If it passes, send the run id and verdict to `lanes/proofs/` as planned.
