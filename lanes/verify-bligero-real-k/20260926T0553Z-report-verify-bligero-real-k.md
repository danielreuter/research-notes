---
lane: verify-bligero-real-k
kind: report
created: 2026-09-26T05:53Z
status: open
---

CHECKPOINT 1b818427 (06:25Z) [open] pins 16/16 also on pod (run r20260926-061022-eac8, pod-built verifier). Input sets re-staged: 3/3 match manifests+cell digests, IR-verified, = prover's staged copies. main reverify can't find nested sweep/*/proofs (ERROR) -> run r20260926-062503-d9c2 calls reverify.verify_tree directly; H100 67fb03cb PASS locally + 5/5 sessions match
CHECKPOINT 1b818427 (06:10Z) [open] 16/16 real-K pins confirmed from main 1b818427 (VM compile + main's release ligero-verify; binary pins each to its own name). No CPU pods anywhere; pod vy-verify-bligero-real-k = A4000 dxkwi6u5039cat ($0.25/h, EUR-IS-1). Next: cells be42c41a c8cc8514 67fb03cb db9f01bf
CHECKPOINT 1b818427 (05:53Z) [open] started (agent bc-30d7a020-fc45-5944-9ceb-1ac513232a9e): non-producer check of 16 real-K pins from main 1b818427, then cells art:be42c41a c8cc8514 67fb03cb db9f01bf; CPU pod, $8
