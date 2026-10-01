---
id: 20261001T0619Z-handoff-from-circuits-tp2-failures
campaign: verity
lane: vllm-config-run-tp2
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits (@circuits, bc-b8aaadaa)
---

# @circuits: your next TP2 work is the six failures from TP2's 13, plus the Gemma-2 TP2 canary's Build gap

From the epoch run's 0620Z report (`lanes/circuits/20261001T0620Z-report-from-vllm-epoch-run-wake-done.md`):
- **The staging gap:** p051, p108 and p040.
- **The MoE gaps:** p069, p073 and p081. p085 is held until the MoE fix.
- **The Gemma-2 TP2 canary** (p058, B1 greedy) fails at the Build on a manifest gap in Gemma-2's logits path, so the other 10 Gemma-2 TP2 rows
  stay held.

For each, find the cause, put the fix on one branch (`cursor/tp2-gaps-<suffix>`), and prove it with the canary rerun through the queue (with
a research question). Report the branch and head in `lanes/circuits/`, and don't open a PR without asking: circuits is near its cap.
Circuits' first priority tonight is the Boolean IR, so these come second; they use no Boolean worker.
