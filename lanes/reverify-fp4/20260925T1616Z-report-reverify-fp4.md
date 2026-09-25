---
lane: reverify-fp4
kind: report
created: 2026-09-25T16:16Z
status: final
---

CHECKPOINT 70097174 (17:07Z) [final] FINAL 70097174: reverify recomputes fp4-nvf4 trees; 6 results accepted (5090 NVFP4 x2, H100 +blake3 x4); equiv art:9b5f1e24 art:c2959a5c registered, need non-producer --check; pod terminated 17:05Z ~$0.14
CHECKPOINT 70097174 (17:01Z) [open] 17:03Z reverify PASS x6, verified=accepted --by reverify-fp4 pushed: 70f275ac (v art:372a815a) 6740eb22 (art:fa407916) 6d067ed3 (art:e5be8bad) f4dc0501 (art:1349ad06) 4d43ab87 (art:de6c7491) 4d151f38 (art:039313a7). instance-equiv art:9b5f1e24 (fp8-hopper-x4 32768) art:c2959a5c (bf16-hopper-x4 8192) registered
CHECKPOINT 65d5b145 (16:49Z) [open] 16:52Z bootstrap OK r20260925-163611-4309; instance_equiv x4 fp8-hopper 32768 + bf16-hopper 8192 running r20260925-164233-1830; reverify 6 results running r20260925-164726-5540 (pod-local store copy, no pod creds)
CHECKPOINT 65d5b145 (16:34Z) [open] pod vy-reverify-fp4 midl24pxz0jind (RTX A5000 SECURE $0.27/h; no CPU stock) created 16:34Z, registered guard 30; syncing lane/reverify-fp4 65d5b145
CHECKPOINT 65d5b145 (16:25Z) [open] 65d5b145 pushed (lane/reverify-fp4): reverify recomputes fp4-nvf4+poseidon2 trees; 18 reverify tests green (5 fp4 negatives). Next: CPU pod, reverify 70f275ac/6740eb22 + 4 blake3-80gb H100, instance_equiv x4 sha256
CHECKPOINT 80b19e59 (16:16Z) [open] started 16:20Z: env ok, reading contract + reverify.py; no pod yet; branch lane/reverify-fp4

# reverify-fp4: fp4-nvf4 committed trees in reverify; six results re-verified; two SHA-256 instance-equiv documents

Inbox at startup: nothing new. Handoffs received: none.

## FINAL
~~~text
tip: lane/reverify-fp4 @ 70097174 (base main@239c0e28)        merge-with: none
known-failures: none    pod: terminated 17:05Z; ~$0.14 (vy-reverify-fp4 midl24pxz0jind, RTX A5000 SECURE $0.27/h, 16:34-17:05Z)
artifacts: art:372a815a art:fa407916 art:e5be8bad art:1349ad06 art:de6c7491 art:039313a7 art:9b5f1e24 art:c2959a5c
~~~
- Code: 65d5b145 makes reverify recompute fp4-nvf4+poseidon2 trees (FP4_HASHED, Poseidon2 over FP4Format lanes). 70097174
  fixes instance_equiv REPO (tool_id printed @unknown on pods). Tests: reverify_test 18 passed (6 new fp4).
- Accepted, `verified=accepted --by reverify-fp4`: art:70f275ac -> art:372a815a, art:6740eb22 -> art:fa407916,
  art:6d067ed3 -> art:e5be8bad, art:f4dc0501 -> art:1349ad06, art:4d43ab87 -> art:de6c7491, art:4d151f38 -> art:039313a7.
  Runs: bootstrap r20260925-163611-4309, reverify r20260925-164726-5540.
- instance-equiv/v1: art:9b5f1e24 (fp8-hopper-x4, 32768) and art:c2959a5c (bf16-hopper-x4, 8192), both equal=true (run
  r20260925-164233-1830; producer-side `--check` r20260925-170149-962a reproduces both). They're not labelled verified: I
  produced them, so my verdict wouldn't count. A non-producer must run a fresh-pod `--check`.
- The 20-equiv.sh run shows as failed only because its own trailing `--check` used the default --vus 4096.
  r20260925-164649-c212 and r20260925-170125-eb1a are empty runs: the script hadn't reached the pod yet.
- Handoff sent: coordinator/20260925T1706Z-handoff-from-reverify-fp4.md (merge-ready + proof_class list + the equiv verification request).
- Scripts: evidence/pod-scripts/{10-reverify,20-equiv,21-equiv-check}.sh.
