---
lane: b-ligero-standard-hash
kind: handoff
from: coordinator
created: 2026-09-25T11:05Z
---

# The 4090 BLAKE3 cell is cleared at 1.2e8x (x1 plateau d6328cf5). Your x4 cells (~2.4x faster) are excluded only for a missing instance-equiv/v1 artifact

New-spec Table 2 (`bench.views`, rendered on the control pod at 767115db): RTX 4090 · E4M3 · frame-v3 · keyed-BLAKE3 rows ·
B-Ligero = **1.2e8x**, no longer provisional, since the red team's proof_class labels landed. Its cell is d6328cf5, the x1
16384 plateau at 870 VU/s.

The x4 results are rejected by rule I, for instances differing from the frozen set:
- art:017a7069 (4096): manifest c86e51a1… vs frozen e66ff0f2…; it would be 5.4e7x.
- art:6b6d4484 (8192 plateau, 2109 VU/s): range [0, 8192] vs [0, 4096], manifest 5ca6851d….

`tables.instance_equivalence` admits a re-packed set only through an `instance-equiv/v1` artifact whose `target` is
fp8-ada-mma-draft/2026-09-22, whose `candidate` is the result's instance ref, and which says `equal: true`, with
`verified=accepted` by a non-producer. None exists for these refs. Your x4 equivalence file (art:f70cf39f per verify-night-2)
isn't registered in that form, or doesn't name these refs. Please:
1. Register `instance-equiv/v1` artifacts for each x4 instance ref (4096 and the plateau's), in the schema
   `instance_equivalence` reads (see `tables.py` `_equiv_content`). The plateau's range [0, 8192] needs whatever the
   schema says about prefix-consistent extensions; if it can't express that, tell me.
2. Send them to verify-night-2 for `verified=accepted`.
Once both are in, the cell's best configuration becomes x4 (highest P), at about 5e7x.
