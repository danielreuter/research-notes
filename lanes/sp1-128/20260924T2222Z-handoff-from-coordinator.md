---
lane: sp1-128
kind: handoff
from: coordinator
created: 2026-09-24T22:22Z
---

# Before FINAL: (1) D1/D2 labels "SP1 stock" / "SP1 precompile"; (2) SP1 security stated for a whole proof, per shard secondary

User decisions (22:15Z), both in drilldown.py on your branch; I merge only after they are in:
1. Naming: the two approaches are **SP1 stock** (unmodified) and **SP1 precompile** (the TC_DOT chip). Rename the D1/D2 row
   labels accordingly (e.g. "SP1 stock (relation-only / bare guest)", "SP1 precompile (TC_DOT chip)", and your variant
   "SP1 stock, FRI query count raised"), keeping the matchers working on existing records. Update tests. Table 2's frozen
   footnote in tables.py stays "modified SP1 (TC_DOT chip)": do not edit tables.py (kb/TABLES.md now says how to read it).
2. D1 soundness wording: total SP1's error over ALL shards of a real proof, the same way B-Ligero is totalled over its
   sub-batches, and lead with that whole-proof figure for a representative proof (name it: e.g. the A100 stock cell
   art:7233a6a3, 22 shards: 2^-99.0 additive per shard + log2(22) = about 2^-94.5 per proof). Per-shard 2^-99.0 (and the
   term breakdown) goes second. Same for the raised-query variant (your run's shard count) and for SP1 precompile.
   Also check the variant text: it still says SP1_TARGET_BITS_OF_SECURITY = 134 was compiled in, but 52968887 raised only
   core_fri_config's query count.
Then FINAL as planned (option 2 run + handoff to verify-po). kb/sp1-prover.md already carries the naming line.
