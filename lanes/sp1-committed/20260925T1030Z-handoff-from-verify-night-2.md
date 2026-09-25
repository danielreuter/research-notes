---
lane: sp1-committed
kind: handoff
from: verify-night-2
created: 2026-09-25T10:30Z
---

# verified: art:49695f7c accepted, and every rep shows instance_roots true

The verdict is art:589785169cf45dbfb24ab6e403a282fb4494ef560e9e2c63db4a611784ecd4e6 (preserved), from run r20260925-100420-dc5b.

- **Build:** your b54e42ed host, built on my pod. It reproduces ELF f4fc749f… and vk 0x00989332…3a66.
- **Check:** `committed-verify --batch` against set art:4a6f7602 passes for reps 0–4 (custody from the attempt's run_files
  art:17f1205b). It passes against both my core-only statement and yours.
- **Negatives:** all 7 REJECT.

Note that art:9e3c06bd, the one you handed me, holds only rep 0.

Two committed_vllm tests failed in my build. The cause is the missing vllm_v1 vectors file in my archive; the frame-v3 path is
unaffected.

Your y leaves are the raw FP32 word, while B-Ligero's are `pack_public`, so the y roots differ across backends. I've told the
coordinator.
