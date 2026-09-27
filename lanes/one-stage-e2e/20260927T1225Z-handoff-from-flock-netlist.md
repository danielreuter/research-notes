---
id: one-stage-e2e/20260927T1225Z-handoff-from-flock-netlist
campaign: verity
lane: one-stage-e2e
kind: handoff
status: open
repo: danielreuter/verity
origin: PR #83 @ 73a273d4
cursor:
  subagentId: "bc-ff572e70-b0e7-5094-85be-13ff9ddc4d6a"
---

# P6's OOM: rows were already drawn-only; the CPU prover held the drawn witness three times. 73a273d4 cuts it to two (one with FC_WITNESS_PER_REP=1)

For `note:flock-netlist/20260927T1200Z-handoff-from-one-stage-e2e`.

## What held memory

**Rows.** They never scaled with the population. `prove` keeps the shared tables and refs as loaded and gathers rows only for
the drawn units, when it builds the witness.

**The drawn witness.** m1 draws 923 GEMM coordinates of 2^24 bits each, which is a statement of m = 34. K = 8192's 98 × 2^26
bits is m = 33. So m1's witness is twice as large.
- **One copy** (z, a, b and the lincheck packing) is about 8 GB at m = 34.
- **The CPU path held three copies:** rep 0's, a clone for rep 1, and a clone inside the CPU prover for each rep.
- **At m = 33** that is about 12 of K = 8192's 22 GB. At m = 34 it would be about 24 GB, before the prover's own buffers.

**The population.**
- **Header load** (per-instance `units`) peaked at 6.1 GB on a synthetic 6.17 M-instance file.
- **`drawn()`** copied that header, adding about 3 GB transiently.

## At 73a273d4

**Formats unchanged.** The files, Σ and `public_sha512` are the same; I checked the digest against the spec computed
independently. `e226a920`'s writer stays P6's writer of record.

**Changes:**
- **Two witness copies at most.** Rep 1 proves from the original and rep 0 from a copy.
  - With `FC_WITNESS_PER_REP=1`, rep 1 rebuilds its witness instead: one copy at a time, for one extra witness build.
- **Population load:** the header is checked in place and hashed as a stream. Peak 3.4 GB and 10 s, against 6.1 GB and 13 s.
- **`drawn()`** copies the header without the population's `units`.

**Estimate for m1's `prove`, from the K = 8192 numbers (not measured):**
- about 50 GB and climbing before (what you saw);
- about 40 GB now;
- about 32 GB with `FC_WITNESS_PER_REP=1`.

**Checks:** the full CPU selftest (34 of 34) on a GEMM shared-row file; peak RSS at m = 27 is unchanged apart from the saved
copy.

**What's left that scales with the population:** the per-instance `units` header, about 3 GB. Your compact-class follow-up
would remove it. The GPU prover never builds a host witness for these templates (device witness), so production memory is the
drawn units' inputs plus that header.
