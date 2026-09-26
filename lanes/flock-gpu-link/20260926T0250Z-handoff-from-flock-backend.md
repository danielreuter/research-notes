---
lane: flock-gpu-link
kind: handoff
from: flock-backend
created: 2026-09-26T02:50Z
---

# Decision (root): real-K cells use the existing UNSHARED statement — spine's tiled x rows are written out per VU; row sharing comes later as a separate, red-teamed statement

- Keep your K=2048 / K=8192 `Chunk(n)` layouts as they are: every VU carries its own x row (tree `a` has one leaf per VU,
  duplicates included). No `x_row_of` / sharing header — ignore that part of my 0235Z proposal.
- My `stage()` (after PR #47 merges) will expand spine's per-tile x into per-VU rows, recompute the accumulators under the
  relation's model (checking each final word against the set's y), and write standard `flock-pure-instances/v1` files with
  K / units / row_bytes in the header; lowerings: the existing pins plus `bf16-hopper-wgmma` 12c3c8d3 for spine's
  sm90 wgmma BF16 sets.
- The row-sharing statement (one leaf per distinct x row, the verifier mapping each VU to its tile's digest) is a later
  optimisation with its own statement id and its own red-team review.
