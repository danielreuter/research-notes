---
lane: coordinator
kind: handoff
from: verify-night-2
created: 2026-09-25T11:50Z
---

# verified: x4 4096 instance-equiv/v1 art:6fdeed7e accepted (verdict art:1e5de3b2); x1 +blake3 malloc re-run art:9b80f566 accepted

**art:6fdeed7e, the x4 4096 instance-equiv/v1 document, is `verified=accepted` by verify-night-2.** Verdict
art:1e5de3b2b967cce41ebf8fb113d439009be0e6c160f63cbccc3fe09e1d4b3dbd, preserved.
- **Renderer check:** `tables._equiv_content` at bfb0b928 returns `[]` against both art:017a7069 and art:050ddede.
- **Reproduction:** main 767115db's `--check` (the producer's tool version) re-derives every field except `lane`, the producer
  tag the renderer needs. Arrays x d64fec05, W f7cb2046 and y 27cdcef1 are frozen == candidate, and equal=True.
- **At bfb0b928:** `--check` reports DIFFERS on canonical, frozen and lane. A regeneration shows why:
  - PR #21 reworded the `canonical` prose;
  - it added `recipe` and `seed` to the `frozen` ref;
  - arrays, candidate, equal, schema, target and tool are identical.
  So a doc written before PR #21 won't `--check` byte-clean at bfb0b928, even though the renderer accepts it. If the renderer
  later compares frozen with the new recipe/seed ref, this doc would need a rewrite.
- Runs: r20260925-114006-0f23, r20260925-114237-c64d, r20260925-114541-4f63, and r20260925-114710-b742 (label).

**Malloc-env re-runs (b-ligero 1037Z / 1125Z), at main bfb0b928 with ligero-verify 8941c72d (source unchanged since 767115db):**
- art:9b80f566 (fp8-ada+blake3 4096) is accepted, verdict art:4d3f166e804c8148ee7eb92ed433aa2480a9badc3141b75e56e88a23e725f072.
- Next: art:c9f4a645 (x1 16384, labelled as producer-flagged non-converged), art:050ddede (x4 4096) and art:19be6afa (x4 8192).
  Run r20260925-113930-8e9a.
