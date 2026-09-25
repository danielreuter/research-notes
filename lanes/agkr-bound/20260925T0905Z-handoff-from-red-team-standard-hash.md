---
lane: agkr-bound
kind: handoff
from: red-team-standard-hash
created: 2026-09-25T09:05Z
---

# red-team SH: your 4 pinned roots (frame-v3 sha256/blake3, vllm-v1) reproduce core-only from the frozen sets; the native tree check PASSes; waiting on the hash layers

Evidence: art:8dee00aa5d8566ae3370576c50f087336f90539760af29e31c3a9b16e99a9863. It contains `rtsh_agkr_pins.py`, which
reads your `commitments.rs` PINS and uses only the core, plus a Python mirror of `operand_domain`.

Set, a, b and y roots all match for bf16-ampere+sha256, fp8-hopper+blake3, bf16-ampere+vllm-v1 and fp8-hopper+vllm-v1.
I found nothing wrong in the tree rebuild, the vllm-v1 path shape or framing, or the `domain_digest` check.

When the hash layers land, I will look at these, so please say in the handoff which gadget and layout you use:
- the digest-to-operand binding in-circuit, i.e. that the published limbs are the digests of the same rows the GKR
  layers consume;
- the prefix, padding and absorption offset of that gadget (26 bytes for vllm-v1's pos-leaf, 64 for sha256/row/v1);
- whether the accepted path drops `--allow-unpinned-commitment`.
