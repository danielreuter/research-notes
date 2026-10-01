---
id: 20261001T0222Z-handoff-from-proofs-clean-baselines-first
campaign: verity
lane: proofs-bf16-hill
kind: handoff
status: open
repo: danielreuter/verity
origin: proofs (bc-8416bc72)
---


# In slot 2, first re-run step 0 clean at K=16384, then at K=8192, before any new step

to: proofs-bf16-hill (bc-3d1a7229); cc proofs-verify-overlap (bc-96b9bb72), which hands over slot 2.

- **Why.** Both BF16 baselines at K=8192 (`r20261001-002113-929d`, `-005232-1cc7`) and the one at K=16384
  (`r20261001-002443-22e0`) carry `cpu-slice-shared`. Step 1 at K=16384 is clean (`r20261001-011930-e54c`). So its
  4.57e8 → 1.83e8 compares a clean step against a contended baseline, and part of that gain may be the contention.
- **What.** Step 0 at K=16384, then at K=8192, on a pod started after 6:52 PM PDT, with `CPUS=16` and staging in a 0-GPU
  job (`note:20261001T0216Z-handoff-from-proofs-provers-floor-and-slices-proofs-bf16-hill`).
- **Then** carry on with the steps already staged (K=8192, 4096, the 2048 tile).
- Checkpoint one line with the two clean overheads.
