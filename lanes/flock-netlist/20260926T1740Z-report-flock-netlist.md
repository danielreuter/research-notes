---
id: 20260926T1740Z-report-flock-netlist
campaign: boolean-escape-hatch
lane: flock-netlist
kind: report
status: open
repo: danielreuter/verity
origin: cursor/flock-netlist-m0-4d6a
branch: cursor/flock-netlist-m0-4d6a
---

CHECKPOINT 9fd167e1 (17:40Z) [open] started M0: verity/flock-netlist/v1 CPU statement landed (RoPE 19/19 CPU selftest cases incl relabelled netlist, SiLU in-circuit parent tree); next GPU device witness + multi-range fold; branch cursor/flock-netlist-m0-4d6a; agent bc-ff572e70
# flock-netlist: M0 `verity/flock-netlist/v1` (NON_ZK, ZK-ready)

Spec: Project store `docs/boolean-prover-scoping.md` (M0 row, M0 acceptance, section 4). Agent bc-ff572e70-b0e7-5094-85be-13ff9ddc4d6a.

## Design (as built)

- One or more whole VUs per block; every glue inside a block is a copy constraint (Δ); no prover-supplied value, no glue claim.
- Slot types per block: BLAKE3 compressions (chunk runs per port; for a multi-chunk port its parent tree, root first), the
  template's units, a reserved mask slot (free cells, A = B = I), forced-zero padding apart from it.
- Public: frame-v3 roots, the row digests (serving leaves; unsalted until Daniel's call), declared outputs, the pinned layout.
  Chaining values, chunk values, every word between slots: private.
- The pinned composite netlist (`flock-netlist/v1`, sha256 = pin) is the meaning: META (ports, ranges, compression roles, leaf
  and output maps, pinned padding-instance values, leaf-commitment scheme) + each slot type's `flock-ir-unit/v2` netlist. The
  verifier derives Δ, regions and values from it and its own public file (no rows).
- Code: `backends/flock/python/verity_flock/netlist.py`, `backends/flock/live/src/{netlist,zk_hooks}.rs`, `bin/flock-netlist.rs`.

