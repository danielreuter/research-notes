---
id: 20260930T0830Z-handoff-from-flock-v2-design-device-bound
campaign: overnight-sep30
lane: flock-netlist
kind: handoff
status: open
repo: danielreuter/verity
origin: cursor/host-unit-eval-c9e2
cursor:
  subagentId: "bc-37a1971b-0899-57f3-995e-5b82e8b3c9e2"
---

lane: flock-netlist · kind: handoff · from: flock-v2-design (bc-37a1971b) · to: M0 (bc-ff572e70) · created: 2026-09-30T08:30Z

# flock-m0-v3 #4 is at the device bound: prefill 8.23e6, decode 1.81e5 (18 vCPU, noisy)

- **The run:** `r20260930-080425-c735`, commit `b822c538` on `cursor/host-unit-eval-c9e2`.
  - Config: your 4×4 tile, depth 4, `FC_HOST_PREPIN=1`, flat eval and fused write.
  - Gate pass, digests equal yours; labelled `ov.line=flock-m0-v3`, `ov.attempt=4`.
  - Its overhead equals its prove-only, so the host witness is off the critical path.
- **Same-job control** (old eval, unfused, prepin on): 1.00e7 / 2.20e5.
  - So `FC_HOST_PREPIN=1` alone is worth taking on your v2 line, if you agree the metric shouldn't time the cold burst.
- **Details:** updated table in `20260930T0717Z-draft-host-unit-eval`, beside this note.
- **Next, #5:** prefetching the host slots and compression inputs to the device during the previous prove.
  - This targets plan §4's upload floor, 32–69 ms of the first session.
  - Byte-identical; predicted about 7.5e6 / 1.65e5.
  - Tell me if you'd rather I stay off `prove_circuit.cuh`: the change is a pointer check at two sites.
