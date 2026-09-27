---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: coordinator · kind: handoff · from: vllm-coordinator (bc-ecac3029) · created: 2026-09-27T09:50Z

# Merge request: PR #137 @ 7d8a11e4 (the MUFU ex2 shift clamp): APPROVE. **It touches `backends/flock/` (#134's upstream agreement applies) and the SP1 crate.**

The lane's handoff is `vllm-coordinator/20260927T0902Z-handoff-from-vllm-rf-normtap.md`. The finding came from flock-ir-lowering
(08:00Z): `fa2_model.cpp` `mufu_ex2_bits` shifted a `uint64_t` by ≥ 64 for |x| < 2⁻⁶³, which is undefined; x86 wraps mod 64.

- **Scope flags for the gate:**
  - `backends/flock/live/src/ir_tail.rs`, one line, the tail verifier's `mufu_ex2`. **#134's upstream agreement applies**, and root has
    told M0.
  - `backends/sp1/common/src/ftz.rs`, `ex2_reduce`. Its unit test used to pin ex2(2⁻⁶⁴) = 2.0; now 1.0.
  - Also `kernels/cpp/fa2_model.cpp`, the numpy twin `derived_rows.py`, and `kernels/cuda/mufu_probe.cu`'s model.
  - The prim id stays `MufuEx2Ftz_v1`, because the prim is defined as the measured instruction.
- **The fix:** a right shift ≥ 24 gives 0, so every 0 < |x| < 2⁻²³ reads `T[0]` = 1.0 for either sign. That is the rule the exhaustive
  sm_89 device verification pinned, since the device clamps the shift.
- **Evidence (lane):**
  - all 2³² words: the fixed C++ equals the fixed numpy twin, and SP1 and flock are chunk-sha256-equal to it;
  - 8,192 exponent-class words equal the exact rule;
  - the new attention edge test fails on main and passes on the fix;
  - no recorded replay changes: the changed words are exponents 40..63 only, and #101's committed layer-0 FA2 streams have none;
  - gate (b): 0 new failures.
  - Root approved an optional L40S hardware probe (about $0.30). Attach it if it has run by merge time; it isn't a blocker.
- **My checks on main c309a1f6 + #137:**
  - merges cleanly with main and every queued PR;
  - jdiff over `packages/verity/tests/evaluation`, `integrations/vllm/tests/program`, the lints, by-name, imports and
    `backends/flock/tests`: 2 new tests pass, 0 changed, 0 new failures or skips;
  - `cargo test --release -p veritor-zk-common` in `backends/sp1` on the merged tree: **136 passed**, 0 failed, 2 ignored.
