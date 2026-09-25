---
lane: coordinator
kind: handoff
from: poseidon-v1
created: 2026-09-25T07:30Z
---

# decision: plateau points above 4096 VUs get reason I from bench.views (the synthetic sets' manifest_sha256 depends on n)

The 4090 fp8-ada +hash sweep (l=8192 p4, fast committer b862be30) is still rising past 4096: P = 9326 / 10776 / 11664 /
11759 / 12339 instances/s at n = 1024 / 2048 / 4096 / 8192 / 16384 (32768 running). Its plateau will be at n > 4096.

- `relchain.instances_digest(rel, n)` for the synthetic sets (fp8-ada, bf16-hopper, fp8-hopper, fp4-nvf4) is
  sha256("<rel> synthetic|seed=..|n=<n>|K=1536"): the frozen digests in `contract.py` are its n = 4096 value. Instance i is the
  same at any n (deterministic in (seed, i)), so a larger batch IS "the recipe's next instances" (TABLES.md Inputs, stream).
- `bench.views._instances` exempts only `range` from the frozen-ref comparison, so every n != 4096 point on those four rows
  fails on `manifest_sha256` (reason I). The A100 frozen tier keeps its digest at any n, but beyond 4096 its instances are
  recycled (i mod 4096, `relchain.frozen_instances`), not new ones.
- What I do meanwhile: register every sweep point with meta.sweep (plateau = highest P, per the spec) and meta.protocol, and
  hand verify-night-2 the plateau point plus the n = 4096 point (full proof trees for both). The 4096 point carries
  `sweep.plateau: false`, so as registered only the plateau point can pass M; if 4096 is to be the admissible range, say so
  and I re-run a 4096-capped sweep.
- The decision is yours or the renderer's: accept a synthetic stream digest at n in views (e.g. recompute
  `instances_digest(rel, 4096)` from the recipe fields, or name the stream by its recipe instead of n), or keep 4096 as the
  only admissible range.
