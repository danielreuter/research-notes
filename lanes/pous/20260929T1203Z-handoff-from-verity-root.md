---
id: 20260929T1203Z-handoff-from-verity-root
campaign: verity
lane: pous
kind: handoff
status: open
repo: danielreuter/verity
origin: verity-root
---

# root -> POUS: `vy-pous-check364` extended to 18:00Z; #408 with the Flock red team; X-SPC-84 with the work-law lane

- **`vy-pous-check364`:** approved to 18:00Z at the same $1.50 cap and 2 pod-hours, within the POUS window. The research coordinator makes the change in `budgets.toml`. Launch after your layout-A red team's go, as planned.
- **#408 at `b2f8db97`:** bc-f0bc7e75 has the grant request, and it reviews from a relayed bundle. I pointed out that `workRule_eq_draw`'s and `countRule_eq_draw`'s records grow. Don't move the head until the verdict arrives. Then file a merge request in `internal/lanes/coordinator/`; it needs `lean-agreement`.
- **X-SPC-84 (strata form):** the work-law lane (bc-0b392ca4), which owns #362's draw law, is answering whether #364 should keep two strata or use one per template. Its answer will come as a separate file in this folder.
- **Tier-3 pilot:** it's on Daniel's decision list for this morning. Nothing in the Python call path moves until he decides.
- **Replay gotcha:** noted for the Lean lanes, thanks. Using `rw` and `show` instead of `simp` where `simp` generates duplicate helper lemmas.
- **Main now:** `0c444ee2`. T12 (#390, #394, refinement #264–#278) has landed. #402, #392 and #406 (with #396) are in train T13.
