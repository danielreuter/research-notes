20260930T1707Z start: reading native_collect bounded staging on 9920af53
20260930T1713Z root cause: throwaway_requests drops per-request seed -> warm-up unseeded -> no runner.sampler/seed (8 B) in plans; fix pushed cursor/warmup-seeded-plans-c646@6a7ff652
20260930T1800Z job 312 sb-g253-fix4 (135M Gumbel B1 + fix) submitted; earlier 289/296/306 died on submit config (untracked workload, VERITY_QWORD_MAX_GATES[_ALLOWED]), not the bug
20260930T1815Z PROVED 135M Gumbel B1 256/32 with fix: commit PASS replay 460/460, run root 03e0337d5e2c6702, run r20260930-180949-a0f0; next 360M Gumbel root identity vs g252 56c5ce0a
20260930T1853Z PROVED 360M Gumbel root identical under fix (56c5ce0a, run r20260930-184721-9a2a vs g252 r20260930-161651-e988); handoff written (coordinator + epoch-run copies); git auth expired, proof-branch bundle in artifacts/
20260930T2024Z start: gumbel B8 splits (g211)
