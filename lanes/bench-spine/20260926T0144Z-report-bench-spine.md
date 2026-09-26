---
lane: bench-spine
kind: report
created: 2026-09-26T01:44Z
status: open
---

CHECKPOINT 3148fabf (02:24Z) [open] WAITING r20260926-021036-5fc3 on vy-bench-spine, check after 02:45Z; agent bc-59ec80ac-9f28-57a3-b488-23d3b5ed5777; next: fetch --all, compare content digests with evidence/20260926T0225Z-suite101-local.json, append to the 0228Z handoff, terminate vy-bench-spine. PR #47 merge-ready (tip 3148fabf, handoff lanes/coordinator/20260926T0228Z-handoff-from-bench-spine.md)
CHECKPOINT 95114837 (02:10Z) [open] pod vy-bench-spine (y8l50t1b7qhbe6, RTX A5000 used as a CPU box, $0.27/h; no CPU pods available) for the second-machine regeneration of the #101 synthetic suite; PR #47 draft (spine code + tests); captured #101 sets: 11,040/11,040 instances re-evaluate bit-exactly through the IR evaluator
CHECKPOINT 35560c88 (01:44Z) [open] bench-spine lane open (agent bc-59ec80ac): input-set generator (IR, seeded, #42 layout), one cell entry point (backend x statement x input set) wrapping the per-backend scripts, per-template lowering registries per backend; branch cursor/bench-spine-5777 (cloud branch policy, not lane/bench-spine); CPU only so far, no pods
