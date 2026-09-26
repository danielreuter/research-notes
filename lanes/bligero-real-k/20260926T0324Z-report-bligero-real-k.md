---
lane: bligero-real-k
kind: report
created: 2026-09-26T03:24Z
status: open
---

CHECKPOINT 05dd4b0a (04:44Z) [open] gates r20260926-042639-c562 (L40S): BF16 xob 4/4 pass so far (8 honest + 86 negatives each, pinned fixture verify); A100 cell k2048 xob captured: prover r20260926-043140-0ebf (p0 1818, p1 2036 VU/s), verifier r20260926-041624-7d7b; H100 cell k2048 xob wgmma-synthetic: prover r20260926-044250-32d3, verifier r20260926-044142-221f (AP-IN-1, H100 only there); handoff 0437Z (interaction check decision); ~$11/h burn
CHECKPOINT 32c5b2fe (04:26Z) [open] branch cursor/bligero-real-k-1521 @ 32c5b2fe (cloud policy, not lane/*): 16 real-K systems pinned (VM compile, evidence/pins-vm-compile.json); gates r20260926-041503-45cd on vy-bligero-real-k-gate (L40S); cell A100 bf16-ampere-x4-k2048+blake3-xob captured #101: verifier r20260926-041624-7d7b, prover r20260926-041646-ed76; pods a100+verifier(A100 PCIe, no CPU pods) US-KS-2
CHECKPOINT 7289e3ad (03:24Z) [open] started: branch lane/bligero-real-k from origin/main 7289e3ad; agent bc-12867b52-c459-52c5-9fd4-c9e425aa1521; plan: K-param x4 relations (-k2048/-k8192), BLAKE3 leaf sized to row chunks, b_interactive bench.cell driver (live verifier pod, RTT+loopback probes); no pods yet
