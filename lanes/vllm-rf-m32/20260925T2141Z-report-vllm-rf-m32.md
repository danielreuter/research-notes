---
lane: vllm-rf-m32
kind: report
created: 2026-09-25T21:41Z
status: open
---

CHECKPOINT 271a0952 (22:49Z) [open] MINT key deleted 22:47:08Z (vyv-rf-m32-reg, prefetch 26/26). gate (a) run 395b died at collection (no sampled_proofs path); restarted. WAIT vyv-rf-m32-reg r20260925-224745-e739 check-back 00:50Z agent bc-7039be6c-2a9f-5501-af51-ee96bf96b428: gate (a) T0+T1 on main 5f8d8789 + jdiff vs a23b
CHECKPOINT 271a0952 (22:43Z) [open] task 2 gate (a) on main 5f8d8789. MINT 22:40:00Z on VM, pod vyv-rf-m32-reg, ttl 3h, object-read-only, prefixes manifests/ objects/sha256/; deleted by prefetch trap (time on wake). WAIT vyv-rf-m32-reg r20260925-224008-395b check-back 01:00Z agent bc-7039be6c-2a9f-5501-af51-ee96bf96b428: prefetch + gate (a) T0+T1 + jdiff vs a23b
CHECKPOINT 271a0952 (22:38Z) [open] fix READY (271a0952; gate b 0 new failures/skips, run r20260925-214510-4478 PRESERVED); vyv-rf-m32-cpu terminated 22:39Z; merge-ready + epoch handoffs sent; starting task 2: gate (a) T0+T1 on origin/main 5f8d8789
CHECKPOINT 271a0952 (21:46Z) [open] fix 271a0952 pushed (scheme.chunk_header M & 0xFFFFFFFF + 2 tests); WAIT vyv-rf-m32-cpu r20260925-214510-4478 check-back 23:15Z agent bc-7039be6c-2a9f-5501-af51-ee96bf96b428: bootstrap + targeted tests + lints + gate (b) base then head + jdiff
CHECKPOINT 78b8935b (21:41Z) [open] opened by agent bc-7039be6c on lane/vllm-rf-m32 from origin/main 78b8935b; fixing fa2h chunk_header M mod 2^32
