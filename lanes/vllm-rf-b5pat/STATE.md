---
id: vllm-rf-b5pat/state
lane: vllm-rf-b5pat
kind: state
created: 2026-09-25T11:24Z
updated: 2026-09-25T12:20Z
---
# vllm-rf-b5pat: split observe/fold/patterns.py into observe/fold/patterns/ (state)

> **COORDINATOR, 12:26Z, URGENT (laptop disk at 1.5 GiB):** STOP `research fetch --all` and every other laptop-side fetch or copy of run outputs, now. Launch new runs with `research run --on ... --custody-r2`: the pod publishes the attempt and every run file to R2 itself, and the pod guard accepts that. Inspect results on the pod (ssh) or read them from R2; plain `research fetch {run}` is for status only. Keep XML and evidence in your notes under about 5 MB. Remove local copies you already fetched only once R2 has them.

> **Coordinator, 11:31Z: the vyv- pod deadline is now 2026-09-25T15:30Z (8:30 AM PT)**, extended in steps of at most 4 h while the coordinator runs; register results as they land.

- a4 base: 10996616
- Worktree: `~/projects/verity-wt/rf-b5pat`, branch `lane/vllm-rf-b5pat`. Base tree for shipping: detached worktree
  `~/projects/verity-wt/rf-b5pat-base` at 10996616 (remove once shipped; laptop disk is at 2 GB free).
- Coordinator: vLLM coordinator (Cursor agent bc-ba6cec03). Brief: `../vllm-refactor/WAVE2_BRIEF.md`.
- Scope (from the prompt): B5 split of the fold's kernel-pattern module into `observe/fold/patterns/`, one module per
  kernel family; `tp/collective_pattern` (now `observe/fold/collective_pattern.py`) goes there too. Pure structure;
  importers updated, no shims; P10 entries leave the ratchet; P8 entries move with their code; no allowlist grows.
- Budget: $15 of pod spend, CPU pods only (cpu3g gate (b) + re-folds; cpu3m 512 GB gate (a)).

## Done
- 11:24Z worktree created at 10996616.
- 11:59Z `ff7a0f8c` (pushed): `patterns.py` (1903 lines) -> `patterns/{resolutions,ops,geometry,transparent,target,gemm,norms,
  rotary,kv_cache,attention,activations,embedding,sampling}.py` + `__init__.py`. All 84 top-level statements moved verbatim
  (source lines and AST identical: `tools/verify_split.py`); only the six section banners dropped. `__init__` re-exports
  exactly the 56 names callers import (incl. resolver's `PerRow`, `Shared`), no `__all__` (string literals would be P8
  layer-class facts). P10 `<module>` 1903 deleted (largest new module sampling.py 582); 7 P11 entries re-keyed, counts equal.
- 12:04Z `ba852261` (pushed): `patterns_fp8.py` -> `patterns/fp8.py`, `collective_pattern.py` -> `patterns/collectives.py`
  (git mv; imports now from siblings). Import lines changed in `engine/profiles/generic.py`, the lazy import in
  `vllm_d9105ea80_sm89_eager.py`, 4 tests. P8 (1), P9 (2), P11 (3) entries moved, counts equal. README observe/ line.
- Laptop checks: pyflakes clean (only `__init__` re-export warnings); P8/P10/P11 per-file scans (stdlib) give exactly the
  moved keys; allowlist entry counts: p08 300=300, p09 177=177, p10 76->75, p11 715=715.

## Pods
- `vyv-rf-b5pat-cpu` = RunPod `andiw61o3shls8` (cpu3g 16 vCPU / 64 GB, 80 GB, $0.64/h), created ~12:10Z (registered by hand:
  the create command died before `--register`).
- `vyv-rf-b5pat-big` = RunPod `8n2373g922sb59` (cpu3m 32 vCPU / 256 GB, 200 GB, $1.76/h, host EPYC 7702P), created 12:13Z.
  cpu3m x64 and cpu5m x64 (512 GB) returned "no instances available" at 12:10-12:12Z.
- 12:15Z bootstrap (`pod_bootstrap.sh --cpu` + pytest-xdist 3.8.0, xgrammar 0.2.7, googleapis-common-protos 1.75.3,
  uvicorn 0.53.0) started on both via `research run --on ... --source rf-b5pat` (ships head `ba852261`).

## Next
- big: prefetch the 26 fixture artifacts with a laptop-minted ro key, delete the key, gate (a) T0+T1 at head with
  `--no-sampler` (b5gm found the PSS sampler ~2x slower); compare test by test with a23b's same-pod base XML.
- cpu: ship base; lints at head; gate (b) head then base; fold/pattern tests from those XMLs; #101 re-fold at head and
  base (its capture log is the only one in the fixtures); code identities before/after.

## Open questions
- (none)

## Found, not fixed
- `properties/protected.py:38` (b2v's) still lists `verity_vllm/observe/fold/patterns.py`; `verity_vllm/*` in the same
  tuple already covers the package, so nothing changes. Left for b2v.
- Prose naming the old files (a4's rule: bare file names are not rewritten): `resolver.py:181`, `census.py:31,53`,
  `patterns_prefix.py:3`, `registry/quarantine/collective/__init__.py:14`, `engine/profiles/generic.py:15`.
