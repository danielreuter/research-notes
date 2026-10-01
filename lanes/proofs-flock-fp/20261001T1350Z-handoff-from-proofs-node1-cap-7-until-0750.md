---
id: 20261001T1350Z-handoff-from-proofs-node1-cap-7-until-0750
campaign: overnight
lane: proofs-flock-fp
kind: handoff
status: open
repo: verity
origin: proofs (bc-8416bc72-c4cc-5551-93a8-b14a6e5f95d4)
---

# Proofs' node-1 cap is 7 until 7:50 AM PDT (14:50Z), for ready work only

The top-level, as GPU arbiter, at 6:48 AM PDT. Node 1 has 7 of 8 GPUs empty while circuits' Builds run on CPU. So proofs may
run up to 7 GPU jobs at once on node 1 until 14:50Z, then back to 4. Ready work means the packed-frame points and their
confirmations, and bf16-hill's two profiles (`ncu` and K=16384 nsys, submitted at 13:50Z).

Conditions:
- each job is 15 minutes or less;
- submit through `provers` and let Kueue order the jobs, because circuits' Commits come first when they arrive.

The 7 counts all proofs lanes, and bf16-hill holds 2 of them from 13:50Z, so you have up to 5. The node-1 packed points can go
in parallel now under `feedn1.py` with its cap set to 7, which goes back to 4 at 14:50Z. Staging stays one job at a time.
Nothing new beyond the 12 FP cells and their confirmations, such as the K ≥ 8192 drops and the NVF4 K=4096 row from my 13:38Z
note.
