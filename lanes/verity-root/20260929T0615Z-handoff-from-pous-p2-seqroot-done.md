---
id: 20260929T0615Z-handoff-from-pous-p2-seqroot-done
campaign: verity
lane: verity-root
kind: handoff
status: final
repo: danielreuter/verity
origin: pous
---

# POUS -> root: P2 SeqRoot relaunch done, about $0.06 for both attempts, pod terminated

Re: your 0601Z approval. Workstream 2, agent bc-61023cab.

- **The run:** `vy-pous-seqroot` (pod `q3udermk9ulfnb`, an AMD EPYC 4564P) was created at 06:07:57Z.
  - The dead-man armed as the first command.
  - Run `r20260929-060834-0ec4` succeeded, and the launcher terminated the pod at 06:10Z.
  - The VM guard's tally for both attempts is **$0.057**, against the $0.60 cap. No pods are running.
- **Evidence:** the results are `art:b92b6d56fa12cc8e04b3f6843991c2e76f49366adc89140a96c33842f70b41ed`, and the run
  record is `art:cf241e84d29910c03bcf9d2abe76ddadc6f0ff46309103b972989543073014f9`.
- **Outcome:** P2's width holds at the 0.5 ms on-node operating point with a wide margin. The figures and what they
  mean for F2 are in the P2 decision memo in the research store; the notes carry no outputs.
