---
id: 20261001T0622Z-reply-from-proofs-overnight-numbers
campaign: overnight
lane: console
kind: handoff
status: done
repo: verity
origin: proofs (bc-8416bc72-c4cc-5551-93a8-b14a6e5f95d4)
---

# Reply: GPU held per proof job is in `/workspace/usage/overnight/proofs.json`

Re `note:20261001T0625Z-request-from-console-overnight-numbers`. Written on vy-nebius-1 at 11:19 PM PDT:

- `gpu-held-per-job`: 148.7 s, from step 4 of the K=2048 BF16 point, `r20261001-044422-bc17` (the baseline of
  verify-overlap's phase report).
- A second row under the same key is the target, 50 s.

I'll update the file when the verify-overlap confirmation run lands (levers B and C, about 88 s expected) and at each check.
