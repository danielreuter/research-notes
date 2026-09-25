---
lane: verify-night-2
kind: handoff
from: b-ligero-standard-hash
created: 2026-09-25T11:42Z
---

# Please verify art:6fdeed7e, the instance-equiv/v1 document for the x4 4096 cell (coordinator 1105Z / 1114Z)

**art:6fdeed7efc48da01c5c84b0e910c358bab725f01abdf2a79888d47ef25f47bc5**, kind instance-equiv/v1, PRESERVED. The document
is the artifact's meta, plus `lane: b-ligero-standard-hash`. I did not edit f70cf39f.

- Made by fused-phases' tool on the pod, from tree 672b23ae (synced, clean): `python -m verity_numerical.bench.instance_equiv
  --relation fp8-ada-x4 --vus 4096`. Then `--check` on the file: "reproduces; equal=True". Script:
  `lanes/b-ligero-standard-hash/evidence/pod-scripts/42-equiv.sh`; the JSON is in `evidence/equiv/`.
- target fp8-ada-mma-draft/2026-09-22.
- frozen = FROZEN_INSTANCES[target]: e66ff0f2…, [0, 4096].
- candidate = art:017a7069's `workload_fingerprint.instances`: bench-instances-fp8-ada/v1, vu-k1536-fp8-ada, [0, 4096],
  c86e51a1…, seed 20260922, recipe.
- equal true. The arrays match frozen = candidate: x d64fec05ec1f…, W f7cb2046f2fd…, y 27cdcef18aa6….
- `tool` reads `instance_equiv@unknown`. `tool_id()` takes REPO = `parents[4]`, which is `backends/`, not the repo root, so
  it never finds the `.research-source.json` stamp. That is cosmetic, and I've told the coordinator.

To check it independently: re-run `--check` on the meta document on your own pod, at a tree with the tool (main has it).
Once you've marked it `verified=accepted`, art:017a7069 (x4 4096, 5.38e7×) and art:050ddede (x4 4096 with the malloc env,
5.20e7×) carry this candidate ref and pass rule I. The 8192 plateau (art:6b6d4484 / art:19be6afa) does not: the coordinator
is deciding that.
