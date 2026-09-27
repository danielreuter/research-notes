---
id: coordinator/20260927T1110Z-handoff-from-flock-netlist
campaign: verity
lane: coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: PR #83 @ 6cdf8a4c
cursor:
  subagentId: "bc-ff572e70-b0e7-5094-85be-13ff9ddc4d6a"
---

# GEMM re-recorded at its new pin: art:4a80e8cb replaces art:656861cd (69 M unit-AND/s, 16.4 s); spend over estimate

- **GEMM coordinate, K = 2048, 1,024 coordinates:** first attempt passed the interaction check, at source `e226a920`.
  - End to end 16.4 s, against 31.7 s. Witness 14.4 s, against 24.7 s.
  - 1.10 M ANDs per coordinate, so 69 M unit-AND/s, against 35.6 M.
  - The pin moved with the descriptor-id keys; this cell is at it.
- **Headline:** cite `art:02cb7df9` (attention) and `art:4a80e8cb` (GEMM).
- **Pods:**
  - verifier `sqyp6rxnqftcio` terminated;
  - L40S `u7fkacoin4t4m1` draining now: every attempt is preserved, and the store scan takes about 10 min.
- **Spend: about $2.9, over my $2.5 upper estimate.** The GPU selftests of both changed templates ran 35 min, and the first
  drain timed out on its scan. The total is still well inside the cap (about $33 of $150).
- **Next:** attention and GEMM stay host-witness bound. The host converges the tensor-core chains (about 90% of the remaining
  witness), so the next device-witness step is evaluating those chains on the GPU.
