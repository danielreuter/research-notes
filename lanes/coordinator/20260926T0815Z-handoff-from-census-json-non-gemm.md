---
cursor:
  subagentId: "bc-d763c580-ec6d-5c4f-bdc2-da5397f3574a"
lane: coordinator
kind: handoff
from: census-json (bc-d763c580)
to: research coordinator (bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628)
created: 2026-09-26T08:15Z
---

# Non-GEMM statement rows: PR #60 is ready to merge. The render can run after the merge, CPU only; the four cells stay U until red-team-flock-2's labels land

[PR #60](https://github.com/danielreuter/verity/pull/60) (`cursor/non-gemm-rows-574a`). It has main (e7e4fad6, with #59 and #58) merged in, and the bench tests pass (454).

## What it does
C-Flock's four frame-v3 cells on #101 get statement rows in the renderer and the entities JSON, one row per statement:

| Statement | Cell |
|---|---|
| rope-head/d64/neox-bf16 | art:dd27fdab |
| silu-mul/i8192/bf16 | art:8a07b80f |
| rmsnorm-fused-cuda/n2048-eps1e-05/bf16 | art:9563d2c8 |
| rmsnorm-triton/n2048-eps1e-05/bf16 | art:63553a6c |

All four are `+frame-v3/blake3-keyed`. A result's statement comes from its `bench.cell` stamp, else from the fingerprint's `subcircuit`.

**Native N** comes from the census's new memory-bandwidth work model: H100 bandwidth (3.35 TB/s, from the datasheet) divided by bytes per input.

| Template | Bytes per input | At the #101 binding |
|---|---|---|
| rope-head | 6D | 384 B |
| silu-mul | 6I | 48 KiB |
| rmsnorm-fused-cuda | 10N | 20 KiB |
| rmsnorm-triton | 6N | 12 KiB |

The bytes are counted from bench-spine's ports. Each row's footnote states the basis.

**Admission:** these statements are rejected with reason U until the cell carries both a red-team `proof_class` verdict and a non-producer verification. Their inputs must be a registered input set of the same subcircuit, otherwise reason I.

Existing renders and parity are unchanged.

## Render (control pod, after merging #60)

~~~sh
python -m verity_numerical.bench.views --root $ST
~~~

## Things to check in that render
- **Red-team gate:** until red-team-flock-2's `proof_class` labels land, each of the four rows shows "not red-team cleared" (U). Once the labels land, the cells fill with no code change.
- **Statement stamp:** each cell must name its statement. If a cell carries neither a `bench.cell` stamp nor a fingerprint `subcircuit`, it falls back to its target's K = 1536 GEMM row and fails there. A cell that fails that way needs its registration re-stamped.
- **Input sets:** each cell's inputs must match a registered `input-set/v1` or `vllm-vu-set/v1` artifact of that subcircuit. The match is by the set's art or content digest; otherwise the cell gets reason I.
- **Worth a review:** the bytes-per-input model counts every row once per input. In serving, weights and cos/sin rows would be cached, so this is the conservative reading and gives the smallest N. Daniel may want to rule on it.
