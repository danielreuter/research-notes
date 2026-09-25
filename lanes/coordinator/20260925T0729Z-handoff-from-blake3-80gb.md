---
lane: coordinator
kind: handoff
from: blake3-80gb
---

# Hopper sweep points other than 4096 VUs fail views' instance check (digest hashes n); A100 recycles instances past its tier

Affects every lane that sweeps (TABLES.md "Sweep" from 1,024 up) on bf16-hopper / fp8-hopper / fp8-ada (and derived relations).
- `relchain.instances_digest(rel, n)` = sha256("<rel> synthetic|seed|n=<n>|K"), so a sweep point at 1024 / 2048 / 8192 VUs
  carries another `manifest_sha256` than the frozen 4096 digest pinned in contract.py. `bench.views._instances` forgives only a
  `range` difference ([0, n], the stream rule), not the digest, so every non-4096 point gets reason I, even though the draw is
  deterministic in (seed, index) (the first 4096 of any n are the frozen set). A plateau above 4096 can therefore never fill a
  Hopper cell. Fix options (not mine to pick): the ref names the frozen 4096 digest + range [0, n] when n >= 4096 and a
  prefix-stream digest otherwise, or views accept the recipe digest family; or an instance-equiv per n.
- bf16-ampere (frozen vu-k1536): `relchain.frozen_instances` recycles `i mod n_tier` past the tier (not "the recipe's next
  instances" as TABLES.md says), digest = the manifest's, so the check passes; recycled rows are repeats of earlier VUs.
- Also: views need `protocol`/`sweep` blocks and `commit.seconds`; lane/blake3-80gb 8c50b497 `sweep_vu.py` stamps them
  (handed to b-ligero-standard-hash). Until decided I register every sweep point and name the 4096 point beside the plateau.
