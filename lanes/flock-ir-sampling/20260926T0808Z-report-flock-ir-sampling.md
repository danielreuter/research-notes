---
lane: flock-ir-sampling
kind: report
created: 2026-09-26T08:08Z
status: open
---

CHECKPOINT f70c6c77 (08:45Z) [open] WAITING r20260926-084457-7a06 (verifier, vy-flock-ir-sampling-ver2 Dallas L40S) + r20260926-084507-3ae9 (prover, vy-flock-ir-sampling-l40s2 KC L40S) L40S cell gumbel-top-p-token-select/v128256/fp32 @ f70c6c77 (IR6 in), check after 09:10Z; agent bc-0ba89fde-5332-53f9-b622-f1264386f8cb; L40S GPU selftest all-pass r20260926-084023-82c0; next: check+register, red-team request
CHECKPOINT b7cbb4d5 (08:41Z) [open] PR #65 @ c0a1 (verity/flock-ir-sampling/v1): lane unit 5,099 ANDs pinned bc18d145; captured #101 32 rows / 4.1M lanes 0 mismatches + IR evaluator on 8 rows; CPU selftest 17/17; L40S driver 550 can't run CUDA 13.3 (r20260926-083317-b873), replaced; WAITING r20260926-084023-82c0 (L40S KC GPU selftest) + r20260926-084036-c9fc (verifier build, Dallas 11 ms); next: L40S cell
CHECKPOINT c53d9148 (08:08Z) [open] started: lane flock-ir-sampling (agent bc-0ba89fde-5332-53f9-b622-f1264386f8cb), branch cursor/flock-ir-sampling-f8cb off cursor/flock-ir-lowering-c78f@c53d9148 (PR #54 not merged); design: lane units in-circuit, top-p keep + noise native cut words; next: lane pieces + unit
