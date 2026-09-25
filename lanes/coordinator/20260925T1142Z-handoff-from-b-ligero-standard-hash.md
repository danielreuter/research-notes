---
lane: coordinator
kind: handoff
from: b-ligero-standard-hash
created: 2026-09-25T11:42Z
---

# x4 rule I: the instance-equiv/v1 document is registered as art:6fdeed7e and sent to verify-night-2. The 8192 set's first 4096 VUs equal the frozen set.

**1. The 4096 document (your 1105Z / 1114Z).**
- **art:6fdeed7efc48da01c5c84b0e910c358bab725f01abdf2a79888d47ef25f47bc5**, PRESERVED. The meta is the tool's document plus `lane`.
- It was written by `instance_equiv --relation fp8-ada-x4 --vus 4096` at 672b23ae, and `--check` reproduces it.
- It meets every `_equiv_content` condition:
  - schema and target;
  - frozen = FROZEN_INSTANCES[target];
  - candidate = art:017a7069's ref, field for field (c86e51a1…, seed, recipe);
  - equal true;
  - x / W / y: frozen_sha256 = candidate_sha256.
- art:050ddede (x4 4096 with the malloc env, 5.20e7×) carries the same candidate ref, so it passes too.
- It needs verify-night-2's `verified=accepted` (handoff 1142Z).

**2. The 8192 plateau (art:6b6d4484 / art:19be6afa, range [0, 8192], 5ca6851d…).**
- The schema can't express it. `frozen` must equal FROZEN_INSTANCES[target], whose range is [0, 4096]. The tool's
  `frozen_relation` also refuses n = 8192, because no registered relation carries the frozen ref at 8192.
- The facts for a prefix rule are in `lanes/b-ligero-standard-hash/evidence/equiv/prefix-fp8-ada-x4-8192.json`.
  `instances(fp8-ada-x4, 8192)[:4096]` decodes to the frozen set's x / W / y sha256, byte for byte (`prefix_equal: true`,
  42-equiv.sh).
- So x4 at 8192 is a prefix-consistent extension of the frozen 4096 set, in the same sense the x1 plateau's n-keyed set
  is: the same seed and recipe, drawn VU by VU. The x1 lines count through that. If TABLES.md admits it, the equiv schema
  would need a `range` / prefix field (for example `frozen_prefix_of: candidate`, with the prefix sha256 as here); the
  renderer would change, not the data. Your call; I have not registered anything for 8192.

**3. A small tool bug (fused-phases' `bench/instance_equiv.py`).** `REPO = parents[4]` is `backends/`, so `tool_id()` never
finds the stamp and writes `@unknown`, as it does in art:6fdeed7e. It should be `parents[5]`. Not fixed here, because it's
not my file and the rendering doesn't depend on it.

Separately, the x1 +blake3 sweep with the malloc env is done: plateau 16384, 1185 VU/s, e2e 13.821 s, 9.07e7× (art:c9f4a645,
sent to verify-night-2). It's the highest measured point, not a converged one: 32768 was killed (rc -9, host OOM).
