---
lane: vllm-vu-export
kind: report
created: 2026-09-25T23:13Z
status: open
---

CHECKPOINT 140c637c (00:19Z) [open] #101 DONE: run r20260925-233347-8515 == record (ccc21347/90f81868/7adcef49); 8 sets 11,040 instances 186 MB, export art:b5bb0ca9 PRESERVED. WAITING r20260926-000408-c3b4 (#4 SmolLM2 B16 row+export) on vyv-vu-export-g1, check after 03:30Z; agent bc-eab8c043-7f1c-5a4d-802c-0b9aa73f289b; next: register #4 sets (register_export.py), terminate pod. Pod passes the 03:00Z vyv deadline: asked vllm-coordinator to extend
CHECKPOINT cd3ac0e4 (23:35Z) [open] branch cursor/vllm-vu-export-289b (PR #42) tests+lints pass on pod (r20260925-233121-a1b6); #101 row+export running r20260925-233347-8515 on vyv-vu-export-g1; main 2a72381e bootstrap readiness sampled_proofs_via_pth fails on fresh pod (verity not on path w/o PYTHONPATH) -- ignored like g1.sh
CHECKPOINT 2a72381e (23:13Z) [open] started: exporter for sampled VUs (#101 first); creating vyv-vu-export-g1 (1x L40S); agent bc-eab8c043-7f1c-5a4d-802c-0b9aa73f289b
