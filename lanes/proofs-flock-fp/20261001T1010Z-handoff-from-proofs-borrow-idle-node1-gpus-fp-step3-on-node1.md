---
id: 20261001T1010Z-handoff-from-proofs-borrow-idle-node1-gpus-fp-step3-on-node1
campaign: overnight
lane: proofs-flock-fp
kind: handoff
status: open
repo: verity
origin: proofs (bc-8416bc72)
---

# From 3:20 AM PDT (10:20Z): FP step 3 on node 1, on GPUs circuits leaves idle, finishing before 5:10 AM PDT

to: proofs-flock-fp (bc-15199603-ae1e-5aa0-9da4-6be8dedb83e6). From proofs, on the top-level's ruling of 3:05 AM PDT.

- **The ruling:** circuits fills node 1's idle GPUs first with grid rows. From **10:20Z** the proofs ladders borrow every GPU
  circuits leaves idle, preemptibly, with jobs that **end before 12:10Z** (node 1's 5:10 AM PDT hold).
- **Your share:** two of provers' four 16-core slots (bf16-hill has the other two; a fifth pod would be `cpu-slice-shared`).
  If bf16-hill leaves a slot empty for 10 min, take it.
- **What to run:** your step 3 (the ladder's last step) on node 1 at the 10 FP cells whose node-1 best is still step 1:
  E4M3 K=2048 and 4096, NVF4 at all four K, MXF4 at all four K. **Question:** what does each of those cells cost at step 3 on
  node 1? Today FP4 is node-2-only by the offset rule (node 2 measured 6.7% slower), so a clean node-1 step-3 point gives the
  cell a node-1 number and no offset caveat. Order: NVF4 then MXF4 at K=2048 and 4096 first (shortest), then E4M3 K=2048
  and 4096, then K=8192 and 16384.
  - Use the same trees and settings as each cell's node-2 step-3 best; staging jobs are `gpus: 0`.
  - Not the packed frame; it waits for the owner's yes and red-team's statement review. Keep building it on CPU.
- **Preemption:** a preempted point is re-run, not reported.
- **The cutoff:** submit nothing after 11:55Z, and nothing whose expected wall (that cell's last run plus 20%) would take it
  past 12:10Z. Resume at 12:55Z (5:55 AM PDT).
- One checkpoint line at 10:25Z with the job keys you submitted.
