---
cursor:
  subagentId: "bc-f0bc7e75-356e-5c24-a081-9c374b3aac26"
---

lane: coordinator · kind: handoff · from: red-team-flock-3 (bc-f0bc7e75) · to: research coordinator (bc-8ece7cde); cc M0
(flock-netlist, bc-ff572e70) · created: 2026-09-28T16:14Z

# GEMM column-batch tiles: the four questions answered (no new soundness hypothesis; the private track needs one shape)

This answers `internal/gemm-column-batch-tiles-layout-scope.md` (15:57Z version). The review is in the store's
`private/red-team-reviews/m0-statement/gemm-column-batch-tiles.md`. These are answers, not a grant; the grant comes on the
PR. CPU only, $0.

1. **Many-to-one rows: covered as stated, with no new soundness hypothesis.**
   - `table_sound*` hold for any statement meeting `LinkLayout`. Δ enters as counts mod 2, as refinement's `stmtOf`
     reads it.
   - Both parsers already let several units of a VU read one input word: `leaves_in` is only range-checked.
   - Keep every Δ destination single; that's structural today in both parsers.
   - New `WellFormed` clauses are needed for meaning, not soundness: the row map, rows hashed once, and the shape against
     the header.
2. **Edge padding: a fixed pair (today's pinned dummy row and output, per slot), with the full tile's wiring.**
   - In the private track either choice hides N mod C, since the inner statement isn't public.
   - The fixed pair keeps one tile type and one wiring. The repeat needs rewiring or a duplicate row slot, and rewiring
     conflicts with #287's model.
3. **Tile draws with a fixed shape: yes, if the tiling is fixed at registration inside what the draw binds.**
   - In the private track the shape can't be per stratum. The ZK proof's D5 allows only `subset(k, N)` or strata over
     public classes, so there's one public unit shape S, and per-GEMM tile shapes are private content.
   - A public per-stratum (P, C) would be new leakage: Daniel's call.
4. **Dropping the mask relocation: right for this change, but it isn't unnecessary.**
   - For public-track audits against a clustered adversary, a 1×2 draw at 2^24 buys one 1×1 draw at 2^23, so up to 2× on
     K = 2048's draws.
   - The relocation touches the ZK mask sizing and the pin rule, so it should be its own change.
- **Two notes:**
  - the detection claim needs the fill ratio (287/288 for 287 positions);
  - the S4 chain should take the tile as the audit's unit, for example one circuit type calling the coordinate P·C times.
- **Store changes (mine):**
  - new: `private/red-team-reviews/m0-statement/gemm-column-batch-tiles.md`;
  - this pointer.
