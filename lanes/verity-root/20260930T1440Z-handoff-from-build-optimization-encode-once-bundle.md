---
cursor:
  subagentId: "bc-47d0a3ed-166c-5d3b-830d-892cdf106942"
id: 20260930T1440Z-handoff-from-build-optimization-encode-once-bundle
campaign: overnight-sep30
lane: verity-root
kind: handoff
status: open
repo: danielreuter/verity
origin: build-optimization (bc-47d0a3ed)
---

# build-optimization -> root: a bundle to push, `cursor/build-encode-once-6942` at `ebbcf6d1` (a Build v2 implementation win, exact)

**Bundle:** `/cursor/stores/bc-36415049-30db-4fff-a34b-81f0afc0124d/artifacts/cursor-build-encode-once-6942-ebbcf6d1.bundle`
- ref `refs/heads/cursor/build-encode-once-6942`;
- prerequisite main `8a4e1147`.

Push it, and I'll open the PR once it's on GitHub (my token is expired).

**What it does** (`integrations/vllm` only, three commits):
- **The request's descriptor is encoded once.** `derive_report` already encodes the flat Program to take its digest. The writer now
  reuses that descriptor, re-reading annotations as `encode_program` does, since the derive adds provenance after its digest. The
  digest and descriptor size come from one canonical text.
- **Instance rows take `runs()`'s tuples.** `json` writes a tuple exactly as it writes the list the rows used to copy it into.
- **Size-neutral** for P10: `_construct` stays at 159 lines and `derive.py` at 1,012.

**Exact:** on a 2-layer SmolLM2 request derive at LP1024 T127, main `8a4e1147` against the branch:
- `descriptor.json.gz` and `instances.json.gz` decompress byte-identical;
- `result.json`'s program fields are equal: digest `ea7ccb36…`, SHA-512, descriptor bytes and SHA-256, and the correspondence digest.

**Faster:** that derive takes 54.6 s on main and 46.8 s on the branch (−14%). On the build-v1 + key/value-prefix stack the same two changes
give 36.5 → 31.4 s. build-v2 attempt 3 (`r20260930-143104-b8c4`, cores 128–159) measures them on the batch-8 1k row and the six fixed
rows, and its labels go up as each row lands.

**Tests at `ebbcf6d1`:** 91 pass: `tests/lint` (P1–P12), `test_build_instances`, `test_program_view_columns`, `test_cross_call`,
`test_torch_frontend`.
