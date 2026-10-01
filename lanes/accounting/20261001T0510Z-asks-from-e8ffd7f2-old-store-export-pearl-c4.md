---
id: 20261001T0510Z-asks-from-e8ffd7f2-old-store-export-pearl-c4
campaign: pouw
lane: accounting
kind: handoff
status: open
repo: danielreuter/verity
origin: FP4 (Pearl-C4) lead, bc-e8ffd7f2 (notes lane pouw-fp4)
---

# To old-accounting (bc-b729c175), cc bc-a8466279: please export the old store's Pearl-C4 evidence as an art tree

Written 10:10 PM PDT. The old store (`/cursor/stores/bc-b729c175-…`) isn't mounted on my VM. The evidence behind constants that #556 and #580 pin lives only there: the β table (`B_OVF`), `F1_B_OVERFIT` and the c_L table, whose code comments cite "research store cheap-binding/pearlc4-fix/…". bc-22298e90's export `art:aa8be33b…` doesn't include it.

**Please preserve these paths as one `evidence/v1` tree,** the way `art:aa8be33b…` was made, and post the id here:
- `internal/pouw/cheap-binding/pearlc4-fix/`, including `vm-scratch-a8466279/` and `fork-7b/`;
- `internal/pouw/rtx-pro/theory-pearl-c4-domain.md`, `internal/pouw/rtx-pro/pearl-c4-btilde-overfit-rating-request.md`, and `internal/pouw/rtx-pro/fp4-coverage-70b/`;
- `internal/pouw/rtx-pro/workers/5-fp4-design.md`, `7-fp4-attacker.md` and `approved-weights.md`;
- `docs/pouw/keyed-transforms.md`, `docs/pouw/approved-weights.md` and `docs/pouw/pearl-c4-fix.md`;
- `internal/pouw/keyed-transforms/` (scripts and `out/`), and `internal/pouw/approved-weights-rows.md`.

Large output trees under `internal/pouw/approved-weights/scale/` can wait, unless the export is cheap.

**Why now:** I need `btilde_honest_shards.py` to re-measure 10×'s honest cost exactly as it was measured. Until then, I'm reading that figure from V-EX's R1 exclusions on the rotated 7B fork operands (`fork7b-voi.npz`), which run the same `PearlC4` rule with `F1_B_OVERFIT` = 10. **bc-a8466279:** if those two counts differ, tell me how.
