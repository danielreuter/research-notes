---
cursor:
  subagentId: "bc-ff572e70-b0e7-5094-85be-13ff9ddc4d6a"
---

lane: gemm-hash · kind: handoff · from: flock-netlist / M0 (bc-ff572e70) · created: 2026-09-29T16:52Z · re: `docs/gemm-hash-cost-plan.md` §1 and row 1

# The native kernel's residual isn't 1.15 µs per compression: 60–65% of `t.witness_comp` is the host slots' upload

The profile is in `internal/native-sha512-witness-profile.md`. It's on the L40S at m = 34: `r20260929-162842-8e17` (native) and `r20260929-164126-164b` (level pass).

- **`t.witness_comp`'s window also uploads every host slot.** With host units that means each deep unit's `z`, `a` and `b`: 1.007 GB at K = 2,048 and 1.711 GB at K = 8,192, pageable, three copies per slot. That takes 87 and 125 ms per rep.
- **The SHA witness itself** is 32–36 ms and 64 ms native, about 0.48 µs per compression. The level pass is 108 and 157 ms.
- **Why the fit read it as per-compression cost:** both the compressions and the host-slot bytes roughly double between the two shapes.
- **What fixes would give, per rep, for these GEMM coordinates:**
  - pinned, overlapped host slots plus a coalesced rows kernel would give about 50 ms (K = 2,048) and 78 ms (K = 8,192), against 117 and 190 ms now;
  - with `z = a & b` formed on the device instead of uploaded, about 35 and 52 ms.
- **The floor:** about 10 ms isn't reachable here while the units are host-evaluated, because their bytes cross PCIe every rep.
- **For shapes without host units,** the window is the memsets (9.4 ms at m = 34) plus the SHA kernels, so the per-compression figure to use is about 0.48 µs now, and about 0.15–0.2 µs with the coalesced rows kernel.
