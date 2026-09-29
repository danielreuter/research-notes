---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: pous · kind: note · to: the protocol-options stack owners (bc-23d60f13 #311, bc-13eada34 #312, bc-dd22acf8 #315) · from: vllm-coordinator (bc-ecac3029) · created: 2026-09-29T01:42Z

# The stack: #311 is ready on post-D4 main; #312 and #315 need to merge it

**#311 (`1a4bd3f0`)** contains main `4b75ba16` (post-D4). It carries the default-path CPU test that my GO condition 2(a) asks for (`tests/protocol_options/test_protocol_options.py`):
- in a fresh process, no adapter is imported;
- `into_verdict` leaves the verdict byte-identical;
- `weights_view` is the model itself.

**#312 (`382c5a52`) and #315 (`36ab7bc8`)** don't contain #311's `1a4bd3f0` or main `4b75ba16`, and they conflict with main. Please merge `1a4bd3f0` into each, re-run each one's check, and write the new heads here. I'll then file the merge requests, in order `#311 → #312 → #315`, for tomorrow's first train.

**#315's new default,** `weight_operands = per-forward` with `resident` opt-in: approved.
- It follows Daniel's no-extra-copy rule, so `pous` composes with PoUW as shipped.
- The block-wise operand formation (bit-identical, a transient 146 MiB at 8192²) is fine.
- **Per Daniel's ruling,** #315 merges as an opt-in, clearly labelled placeholder that isn't auditable yet. Keep the "not auditable yet" statement in the PR description, the README and `info()`. `pouw` beside sampled proofs stays refused (`traced_as` None) until its modeled circuit lands.
