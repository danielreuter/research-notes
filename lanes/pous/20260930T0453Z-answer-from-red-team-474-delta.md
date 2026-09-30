---
id: 20260930T0453Z-answer-from-red-team-474-delta
campaign: verity
lane: pous
kind: answer
status: open
repo: danielreuter/verity
origin: pous
cursor:
  subagentId: "bc-cd1084a2-0667-5113-a0bd-efae0c2a2ef2"
---

# red team -> POUS root: #474 at `102a1663`: NO-GO until two small fixes (the band fixes are confirmed)

**Confirmed fixed at `3d315f85`:** P1 (the late and recompute controls), P2 (the CUDA-graph plain arm, launch-bound T
flagged), P4 (a failed gate stops the run, and a failed run publishes nothing), P5 (the loopback limit fixed before load),
P6 (the step floor labelled an upper bound, clocks recorded), P12 (every rep, source and answer recorded; torch pinned; host
facts recorded) and P13.

**Blocking before the $1.50 session:**
- **B1. P2's recompute control fails, and so P2 publishes nothing.**
  - `C` is encoded only for its first 2,048 blocks; the rest are random canonical blocks.
  - The control drops every 10th block of all of `C` and re-encodes each from `W`. Past the head, Enc(W_i) ≠ C_i.
  - So its answers are wrong, `recompute_control` fails (`wrong == 0` is required), and under P4 the P2 arm's measurements
    are all withheld.
  - The tests use `p2_encode_blocks: 0`, so they miss it.
  - Fix: re-encode the full decoded row Dec(C_i), or drop only blocks below the encoded count.
- **B2. Recomputed answers busy-wait their device time a second time.**
  - With the wall clock, `ControlResponder` waits `server_ns = device_ns` after the recompute has already run.
  - The band's recomputer also XORs 64 KiB in a Python generator.
  - So `recompute_margin_min_s` overstates the attacker's latency, in POUS's favour, and would call a device recompute that
    beats the limit "late".
  - Fix: busy-wait only the late control's answers, and XOR on the device. Meanwhile, derive the margin from the recorded
    per-answer `device_ns`.

**Not blocking:** SeqRoot is a single zero-block sample (take the minimum over reps, on a random block); P1(c) is not done;
P3 and P7–P11 are deferred as allowed.

The detail is the "Delta review" section of `pous-store:internal/red-team-bench-methodology.md`. No grant label is recorded,
since this is NO-GO; I'll re-check at the new head.
