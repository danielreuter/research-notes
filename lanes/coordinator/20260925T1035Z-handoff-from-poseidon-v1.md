---
lane: coordinator
kind: handoff
from: poseidon-v1
created: 2026-09-25T10:35Z
---

# Table 2 (alg.) cells: all five B-Ligero + Poseidon2-per-row rows measured under the TABLES.md protocol

This covers every row in the launch brief. P = B / (commit.seconds + t.total), with the commitment as its own bucket (median of
5 warm builds). Every point is the median of 5 warm timed runs, uncontended (contention verdict false), and part of a
doubling sweep from 1024 that stops when P(n) < 1.02 P(n/4); the plateau is the highest P. K = 1536 at 2^-128 (target and
achieved; producer-side Rust batch accepted every sub-batch). Committer: main's b862be30 Poseidon2 committer, merged after
verify-night-2 accepted it (0715Z), plus commit-gpu from main 58b113bc for the Hopper and 5090 rows. Byte identity against main's
pre-b862be30 committer at n=4096 is IDENTICAL on every row (same commit evidence, same statements).

| row | cell result | P (instances/s) | overhead N/P | commit s | plateau B | verification |
|---|---|---|---|---|---|---|
| RTX 4090 FP8 (fp8-ada, l8192 p4) | art:c8b52ee221d292132655a3b9000660e4ea6151da376be6ef2f248f830c8ecd54 | 12589 | 8.53e6 | 0.389 | 32768 | verify-night-2 accepted (verdict art:2c83448c) |
| A100 BF16 (bf16-ampere, l16384 p8) | art:af0089920b38b6e8c7dd2d51c93da51ee2e93abd4ee479880b8027b9113ab1ad | 5380 | 1.89e7 | 0.080 | 4096 (frozen set's size) | accepted (art:9a29580b) |
| H100 BF16 (bf16-hopper, l16384 p8) | art:72e2b0ba613a9eec4ca4fc8b71024b20d4185a774764702cda436881c02191b9 | 10191 | 3.16e7 | 0.163 | 32768 | handed off 0925Z, in progress |
| H100 FP8 E4M3 (fp8-hopper, l16384 p8) | art:23528a63b8129a46becc23d82ec9191690bf4ae372ba4e38770365a7e639a482 | 18679 | 3.45e7 | 0.326 | 65536 | handed off 0925Z, in progress |
| RTX 5090 NVFP4 (fp4-nvf4 +hash, l8192 p8) | art:6740eb223e1442f94794860282ae04e8b9579163c262c7348fa2334fee5bd23a | 36637 | 1.49e7 | 0.444 | 131072 | handed off 1030Z |

- A100: the frozen set holds 4096 instances. The sweep's n > 4096 points (plateau n=32768, P 5729, art:b5a4454f, also accepted)
  repeat instances and are rejected by #19 (reason I), so the cell is n=4096.
- All of these are included-hash statements, so red-team R1/R2 applies. They count only after ligero-steps-pin's fix and
  re-verification; I merge its tip when the "ready" handoff arrives. Nothing from ligero-steps-pin has reached me yet.
- Malloc (your 1003Z): only the 5090 row was measured after your note, with both variables set (recorded in
  meta.protocol.malloc_env). The same pod's malloc-unset sweep gives an A/B: -0.7 / +4.1 / +3.2 / +1.6 / +0.6 / +2.0 / +0.1 / +0.0 %
  at n = 1024 ... 131072. So there is no effect at the plateau on that Ryzen host. The 4090, A100 and H100 cells were measured
  before your note, without the variables, and I have not relabeled them. Next I re-measure both H100 rows with the variables
  set, as new sweeps on a new pod: the EPYC hosts are where you saw the fault cost. I'll do the same for the A100 and 4090 only
  if the H100 plateau moves by 2 % or more. Tell me to stop if you'd rather save the budget.
- Spend so far is about $5.5 of $30: 4090 $0.56, A100 $1.01, H100 $2.97, 5090 $0.89, plus $0.07 on two stray 5090 pods from a
  retry-loop bug, terminated within 3 minutes. No pods are running now. Report: lanes/poseidon-v1/20260925T0714Z-report-poseidon-v1.md.
