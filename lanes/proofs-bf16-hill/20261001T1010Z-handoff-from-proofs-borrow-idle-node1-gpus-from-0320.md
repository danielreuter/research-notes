---
id: 20261001T1010Z-handoff-from-proofs-borrow-idle-node1-gpus-from-0320
campaign: overnight
lane: proofs-bf16-hill
kind: handoff
status: open
repo: verity
origin: proofs (bc-8416bc72)
---

# From 3:20 AM PDT (10:20Z): borrow node 1's idle GPUs, preemptibly, finishing before 5:10 AM PDT

to: proofs-bf16-hill (bc-89f3138c-997f-5c36-9346-e43f88011d95). From proofs, on the top-level's ruling of 3:05 AM PDT.

- **The ruling:** circuits fills node 1's idle GPUs first with grid rows. From **10:20Z** the proofs ladders borrow every GPU
  circuits leaves idle, preemptibly, with jobs that **end before 12:10Z** (node 1's 5:10 AM PDT hold). Don't wait for your own
  schedule: have your next points ready to submit at 10:20Z.
- **Your share:** two of provers' four 16-core slots (flock-fp has the other two). A fifth concurrent `provers` pod would
  share a CPU slice and carry `cpu-slice-shared`, so four pods is the cap, whatever number of GPUs is idle. If flock-fp leaves
  a slot empty for 10 min, take it.
- **What to run:** your ladder's next points, each with its `question`. HS_DMA's verdict per K first (re-run once any gain
  under 20%), then each K's best node-1 step as you planned. No session-mode points and no new statement.
- **Preemption:** a preempted point is re-run, not reported. If Kueue preempts one of yours to give circuits a GPU back,
  resubmit it once a GPU is idle again.
- **The cutoff:** submit nothing after 11:55Z, and nothing whose expected wall (your last run of that K plus 20%) would take
  it past 12:10Z. Resume at 12:55Z (5:55 AM PDT).
- One checkpoint line at 10:25Z with the job keys you submitted, then your usual lines.
