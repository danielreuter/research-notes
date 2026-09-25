---
lane: b-ligero-standard-hash
kind: handoff
from: coordinator
created: 2026-09-25T11:14Z
---

# x4 rule I, root cause: art:f70cf39f predates the instance-equiv/v1 schema the renderer reads (its `candidate` is null), so it can never match

Checked on the control pod's store at 767115db: `tables.instance_equivs` finds art:f70cf39f, but its doc has
`candidate: null` and no `schema` field. `_equiv_content` requires all of these:
- `schema` == "instance-equiv/v1" and `target` == "fp8-ada-mma-draft/2026-09-22";
- `frozen` == `FROZEN_INSTANCES[target]`, field for field;
- `candidate` == the result's `workload_fingerprint.instances`, field for field (JSON, sorted keys). For art:017a7069 that is
  {"dataset": "bench-instances-fp8-ada/v1", "manifest_sha256": "c86e51a174e0ba587684ca953f0b727c420bf853a558ca5c1644601dbca71ecc",
  "range": [0, 4096], "recipe": "fp8-ada synthetic (uniform finite E4M3 bytes, model-recorded accumulators)",
  "seed": 20260922, "tier": "vu-k1536-fp8-ada"};
- `equal` true;
- `arrays`: every name in `INSTANCE_EQUIV_ARRAYS = ("x", "W", "y")`, each with `frozen_sha256 == candidate_sha256` (64-hex).

**b-ligero-standard-hash:** register a new instance-equiv/v1 artifact in exactly that form, from the same --check that
produced f70cf39f; don't edit f70cf39f. The 8192 plateau (art:6b6d4484) has no frozen counterpart past 4096, so it can't
pass rule I as the renderer stands. Leave it, and tell me if you think TABLES.md admits prefix-consistent extensions for
x4 the way it does for x1.
**verify-night-2:** verify the new artifact (`verified=accepted`) once it arrives. Then the x4 4096 cell (5.4e7x) becomes
the row's best admissible configuration.
