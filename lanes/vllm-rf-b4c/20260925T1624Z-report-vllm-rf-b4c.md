---
lane: vllm-rf-b4c
kind: report
created: 2026-09-25T16:24Z
status: open
---

CHECKPOINT 9689a1ef (18:09Z) [open] head 9689a1ef (merged a5c 40b9e571, pushed). #101 at 5494e29f = record, nonint 992/992. RUNNING: vyv-rf-b4c-cpu (new) gate(b) head r20260925-180555-f321 / base 40b9e571 r20260925-180449-ed37, check ~18:45Z; g1 #101 at 9689a1ef r20260925-180228-0dda, check ~18:30Z
CHECKPOINT 5494e29f (17:30Z) [open] WAITING on g1 r20260925-172753-d0b2 (FA2 tap rebuild MAX_JOBS=12 after BOOTSTRAP_FAIL_FA2_TAP, then #101 + non-interference at 5494e29f); check back ~18:30Z. gate(b)+lints green; cpu handed to b5vab
CHECKPOINT 5494e29f (17:18Z) [open] HANDOVER vyv-rf-b4b-cpu -> vllm-rf-b5vab (handoff 20260925T1720Z; b4c no longer uses it). g1 still b4c's: FA2 tap build, then #101
CHECKPOINT 5494e29f (17:14Z) [open] gate(b) at 5494e29f vs 38a8d35d same pod: 0 new fail/skip/skip reason, 0 deleted, 17 new pass; lints 47 (base 45). XMLs on b4b-cpu /workspace/b4c/{head,base}. g1: FA2 tap still compiling, then #101
CHECKPOINT 5494e29f (16:56Z) [open] coordinator 16:55Z: merged main 38a8d35d -> lane/vllm-rf-b4c@5494e29f (pushed; b5vab told). gate(b)+lints on b4b-cpu: head r20260925-165436-ee4e, base 38a8d35d r20260925-165256-8dfd (aborted 8b3537d5 base r20260925-164820-0072). g1 bootstrapping (driver 580 OK)
CHECKPOINT 5c05ff6d (16:25Z) [open] succeeding vllm-rf-b4b (bc-892f86c5) after 16:03Z restart; head lane/vllm-rf-b4b@5c05ff6d, no commits yet; adopting vyv-rf-b4b-cpu + vyv-rf-b4b-g1; bootstrapping for c1 re-gate
