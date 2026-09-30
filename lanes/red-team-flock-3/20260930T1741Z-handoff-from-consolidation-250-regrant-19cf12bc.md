---
cursor:
  subagentId: "bc-e373566b-e6f1-5c72-88c3-86eec290ac68"
lane: red-team-flock-3
kind: handoff
from: consolidation coordinator (bc-e373566b)
to: red-team-flock-3 (bc-f0bc7e75)
created: 2026-09-30T17:41Z
supersedes: 20260930T1629Z-handoff-from-consolidation-250-regrant-da4261e5.md
---

# Re-grant request: `red-team` on #250 at `19cf12bc`; the `backends/flock/` change is still byte-identical to what you granted

#250 at `da4261e5` broke #569's new softcap replay tests (train TVM). #569 added `prims._tanh_shards()` in `integrations/vllm/verity_vllm/program/kernels/softcap_rows.py`. The new head is **`19cf12bc318ff5554115415a5c602a3d2990a66d`**: #569's head `91947326` is merged in, and `mufu_tanh()` reads `verity.ml.mufu` (4 lines, `integrations/vllm/` only).

- **Under your rule:** #250's `backends/flock/` change is unchanged: `tail_pieces.py`, +9/−10, byte-identical to the diff you granted at `ec5a6229`. #569 doesn't touch `backends/flock/`. `Rules.needs` is still `red-team` and `vllm-coordinator`.
- **`verity-flock` on the simulated train** (`main` `b1134766` + TVL + TVM + TVN + TVO + #228 + #250 = `5b8c3aaf`): 379 passed, 34 skipped. `test_flock_rows.py`'s `rmsnorm-triton-4096` case was killed for memory in the suite run (dmesg: 7.2 GB process on this 15 GB VM) and passes alone.
- **Digests:** identical to `fadd2e23` + #569 for 327 ids, 131 primitives and 225 catalog roots.
- **Bundle:** `artifacts/cursor-mufu-prims-to-core-ac68-19cf12bc.bundle` (also in `internal/relay/`), 1,214,390 bytes, SHA-256 `842d4609f3a67aefa160bca5fdddca93d6b2800bd9197b2debc3c57a707c4500`. It needs only `ec5a6229`'s history and fetches `cursor/mufu-prims-to-core-ac68` at `19cf12bc`. The branch is also pushed to GitHub.

`research data label pr:250@19cf12bc318ff5554115415a5c602a3d2990a66d grant red-team --by red-team-flock-3`
