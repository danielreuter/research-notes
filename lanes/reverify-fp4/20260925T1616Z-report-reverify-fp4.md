---
lane: reverify-fp4
kind: report
created: 2026-09-25T16:16Z
status: open
---

CHECKPOINT 65d5b145 (16:49Z) [open] 16:52Z bootstrap OK r20260925-163611-4309; instance_equiv x4 fp8-hopper 32768 + bf16-hopper 8192 running r20260925-164233-1830; reverify 6 results running r20260925-164726-5540 (pod-local store copy, no pod creds)
CHECKPOINT 65d5b145 (16:34Z) [open] pod vy-reverify-fp4 midl24pxz0jind (RTX A5000 SECURE $0.27/h; no CPU stock) created 16:34Z, registered guard 30; syncing lane/reverify-fp4 65d5b145
CHECKPOINT 65d5b145 (16:25Z) [open] 65d5b145 pushed (lane/reverify-fp4): reverify recomputes fp4-nvf4+poseidon2 trees; 18 reverify tests green (5 fp4 negatives). Next: CPU pod, reverify 70f275ac/6740eb22 + 4 blake3-80gb H100, instance_equiv x4 sha256
CHECKPOINT 80b19e59 (16:16Z) [open] started 16:20Z: env ok, reading contract + reverify.py; no pod yet; branch lane/reverify-fp4
