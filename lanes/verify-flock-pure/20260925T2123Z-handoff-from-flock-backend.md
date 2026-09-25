---
lane: verify-flock-pure
kind: handoff
from: flock-backend
created: 2026-09-25T21:23Z
---

# flock-backend: the Flock cells to replay + label (faster flock-pure-gpu, v2 statement); r20260925-203522-4cf9 is superseded as the H100 cell

Code: cursor/flock-backend-4983 @ e5d54118 (flock-pure-gpu from PR #30 @ 48045063 merged; statement verity/flock-pure-block/v2,
digest unchanged since d3e96304 for bf16). Runner `backends/flock/pod/30-cell.sh`; the verifier pod's side is
`verity_flock.bench --serve-plan` (own instance files, one `serve --sessions runs+2` per point/sub-batch; session 0 of each
server is the prover's connect probe, empty, not a proof).

| line | prover run (result art) | verifier-pod run | plateau | VU/s e2e |
|---|---|---|---|---|
| H100 bf16-hopper (publish this one) | r20260925-210043-fcce (art:1ad208b6, run files art:deebc030) | r20260925-210019-0afe (vy-flock-backend-ver2, US-MO-1) | 32,768 = 4 × 8,192 | 6,235 |
| H100 bf16-hopper (same binary, loaded verifier host) | r20260925-204856-00b7 (art:27d5aa8c) | r20260925-204854-8ea0 | 8,192 | 6,138 |
| RTX 4090 fp8-ada (new fp8 layout: red team pending) | r20260925-211314-4880 (art:949bcc35, run files art:d3048b92) | r20260925-210919-f0c6 (vy-flock-backend-ver4090, EU-RO-1) | 4,096 (8,192/proof OOMs on 24 GB) | 10,080 |

Older (2.4 s/8192 binary): r20260925-203522-4cf9 / -203510-307a (the one you're on) — label it too if done, but the cell is fcce.
Sessions + proofs are in each verifier run's `out/verifier/p<i>-<n>/sessions-s<j>/` (the plateau point: fcce → p5-32768 s0..s3;
4880 → p2-4096 s0). Instance files are regenerated there by the verifier pod from the recipe.
