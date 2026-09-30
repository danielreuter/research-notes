---
id: 20260930T2038Z-handoff-from-infra-executor-acts
campaign: verity
lane: kueue-fold
kind: handoff
status: open
repo: danielreuter/verity
origin: infra coordinator (bc-17cc41f1)
---

# kueue-fold: step 3 landed. Next, a node-1 executor that acts on grants from the brain, and co-location to free node 1's GPUs

Step 3's Build on node 2 is a real win. Next, taken from gaps 2 and 3 in `note:20260930T2035Z-draft-one-queue-cutover-and-onboarding`:

1. **The node-1 executor acts on the brain's grants,** not only observes them. The brain lives on node 2 (cluster-build's
   decision), and grants arrive over `vy-cluster`. The executor starts each granted job as a Kueue Job or Pod with the
   placement the brain gave it. When the link or the brain is down, it falls back to Kueue's own admission. The job and grant
   interface is agreed with cluster-build in `lanes/cluster-build/`.
2. **Co-location on node 1.** CPU-phase Commits and low-use sweeps must stop pinning whole GPUs. Use your 0-GPU pod with
   `NVIDIA_VISIBLE_DEVICES=all` plus `CUDA_VISIBLE_DEVICES` targeting, and tell circuits exactly how its Commits use it. Measure
   node 1's GPU busy before and after.
3. **Quiet on node 1:** respect M0's quiet hour and the Build benches' quiet needs, together with cluster-build's quiet
   single-GPU class.

Report each step when it lands. Times people read are Pacific.
