---
id: 20261001T0140Z-handoff-from-proofs-gpus-scarce-proofs-verify-overlap
campaign: verity
lane: proofs-verify-overlap
kind: handoff
status: open
repo: danielreuter/verity
origin: proofs (bc-8416bc72)
---

# GPUs are scarce (Daniel, 6:35 PM PDT): hold a GPU only while proving, one per lane, nothing new past tonight's list

to: proofs-flock-fp (bc-6caad52c), proofs-bf16-hill (bc-3d1a7229), proofs-verify-overlap (bc-96b9bb72); the same note is
in each lane.

Circuits' vLLM work gets GPU priority; the split between circuits and proofs is with verity-top. Until it rules:
1. **No GPU held through a CPU phase.** Stage statements in a 0-GPU job, then prove from the stage cache. That's
   proofs-rows' split: byte-identical statements, 3.4 GPU-min saved per miss (recipe:
   `lanes/proofs-n2-guest/20260930T2225Z-handoff-from-proofs-rows-stage-prove-split-recipe.md`). Grafana flagged
   `nd-proofs-flock-f-967e490bab-prover-b-0` holding GPU 0 at 0% for 10 minutes at 6:10 PM PDT.
2. **At most one GPU per lane at a time.**
3. **Finish the points tonight's goals need, and queue nothing beyond them:**
   - flock-fp: NVF4 and MXF4 to K=16384, and re-runs of contended points.
   - bf16-hill: steps on the four K.
   - verify-overlap: the overlap itself.
4. **verify-overlap:** taking the verifier off the GPU's critical path frees the most GPU time in proofs. It stays your
   first priority, ahead of live per-round coins.

Checkpoint one line when your lane complies, or say why it can't.
