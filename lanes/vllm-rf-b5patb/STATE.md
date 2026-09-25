---
id: vllm-rf-b5patb/state
lane: vllm-rf-b5patb
kind: state
created: 2026-09-25T14:08Z
updated: 2026-09-25T14:08Z
---
# vllm-rf-b5patb: split observe/fold/patterns.py into observe/fold/patterns/ (state)

> **Coordinator, 14:27Z: the vyv- pod deadline is now 2026-09-25T18:30Z (11:30 AM PT)**, extended in steps of at most 4 h while the coordinator runs. It replaces every earlier deadline line in this file.

> **Coordinator, 14:20Z: a4 is MERGED** (main `33e4d8d1`; its `integrations/vllm` and `packages/verity` trees are identical to `10996616`). Rebase now: `git fetch origin main && git rebase --onto origin/main 10996616 lane/vllm-rf-b5patb`, then `git push --force-with-lease`. Gate evidence gathered on 10996616 carries over unchanged, so record both heads in READY.md.

> **Successor of b5pat** (bc-c87a1519, hung at the 12:30Z host disconnect). Agent bc-c7bcfa82. Start commit `ba852261`
> (`origin/lane/vllm-rf-b5pat`). The predecessor's worktree `rf-b5pat` and branch `lane/vllm-rf-b5pat` are left alone.

> **Research coordinator, 14:09Z (copied from b5pat's STATE):** STOP every `research fetch` (and `fetch --all`) to the
> laptop. Runs: `research run --on <pod> --project verity --custody-r2 ...`; inspect on the pod (`research pods ssh`) or
> from R2 (`research data preserved <run>`, `research data fetch <art> --path <one small file>`).

> **COORDINATOR, 12:26Z, URGENT (laptop disk):** no `research fetch --all`, no laptop-side fetch of run outputs. New runs use
> `research run --on ... --custody-r2`; inspect on the pod (ssh) or from R2. `research fetch {run}` is for status only.

> **Deadline:** 2026-09-25T17:00Z per LANE_PROMPTS_WAVE2 (extended in steps).

- a4 base: 10996616
- Worktree: `~/projects/verity-wt/rf-b5patb`, branch `lane/vllm-rf-b5patb` (pushed at `ba852261`).
- Coordinator: vLLM coordinator (Cursor agent bc-ba6cec03). Brief: `../vllm-refactor/WAVE2_BRIEF.md`.
- Scope: B5 split of the fold's kernel-pattern module into `observe/fold/patterns/`, one module per kernel family;
  `tp/collective_pattern` (now `observe/fold/collective_pattern.py`) goes there too. Pure structure, match order preserved;
  importers updated, no shims; P10 entries leave the ratchet; P8 entries move with their code; no allowlist grows.
  Acceptance: re-folded record Programs byte-identical, plus gates.
- Budget: what remains of b5pat's $15, CPU pods only.

## Done (predecessor b5pat)
- 11:59Z `ff7a0f8c` (pushed): `patterns.py` (1903 lines) -> `patterns/{resolutions,ops,geometry,transparent,target,gemm,norms,
  rotary,kv_cache,attention,activations,embedding,sampling}.py` + `__init__.py`. All 84 top-level statements moved verbatim
  (source lines and AST identical: `tools/verify_split.py`); only the six section banners dropped. `__init__` re-exports
  exactly the 56 names callers import (incl. resolver's `PerRow`, `Shared`), no `__all__`. P10 `<module>` 1903 deleted;
  7 P11 entries re-keyed, counts equal.
- 12:04Z `ba852261` (pushed): `patterns_fp8.py` -> `patterns/fp8.py`, `collective_pattern.py` -> `patterns/collectives.py`
  (git mv; imports from siblings). Import lines changed in `engine/profiles/generic.py`, the lazy import in
  `vllm_d9105ea80_sm89_eager.py`, 4 tests. P8 (1), P9 (2), P11 (3) entries moved, counts equal. README observe/ line.
- Laptop checks: pyflakes clean; allowlist entry counts: p08 300=300, p09 177=177, p10 76->75, p11 715=715.

## Done (b5patb), from what the predecessor's runs left on the pods
- cpu pod, run `r20260925-122258-1b8d` (cpu_chain.sh, trees `/workspace/research/src/{ba852261…,10996616…}`):
  lints head rc 0 and base rc 0 (12:23-12:24Z); gate (b) head 12:24-12:57Z and base 12:57-13:31Z, both
  `51 failed, 3647 passed, 286 skipped, 6 xfailed, 11 errors`. 14:13Z a1's jdiff on the pod (base vs head): 4001 = 4001,
  0 only-in-base, 0 only-in-head, 0 outcome changes, 0 new failures, 0 new skips or skip reasons
  (`evidence/jdiff_b.txt`). Fold/pattern-related test modules: 207 passed, 1 failed, 5 skipped on both sides (the failure,
  `test_patterns_synthetic::test_gumbel_two_stage_sampler_is_one_token_select`, is identical at base).
- 14:14Z code identities on the cpu pod (a4's `tools/ident.py`): `code_identity` = hot-commit key = research Tools closure
  `3809d208…` (1169 files) -> `e82dbc8b…` (1182 files); `construction_version` and `registry_version` unchanged
  (`evidence/ident-{10996616,ba852261}.json`).
- big pod: prefetch 26 ok / 0 fail, key deleted 12:21:25Z. The predecessor's #101 re-fold (`r20260925-122818-9e8a`) failed
  at both head and base: profile `gen_llama_llama32_1b` (the record's name) no longer exists since P6; the role's
  profile is `derived_LLAMA32_1B`. Nothing was compared.

- 14:19Z #101 re-fold `r20260925-141717-7caf` (big pod, `derived_LLAMA32_1B`): fold digest `cc48449d…` at head, base and in
  the record; `program.json` (`ef5b2fe5…`, 17,119,764 B) and `instances.jsonl` byte-identical head vs base;
  `accesses.jsonl.gz` differs only in the gzip header mtime (decompressed identical); fold_summary / resolution.json differ
  only in timings, utc, paths, RSS. by_pattern 13 patterns / 17,199 matches, same order as the record.
  Evidence `evidence/refold-r101{,-deepdiff}.txt`.
- 14:22Z a4 merged into main (`33e4d8d1`, 14:13:54Z). Rebased `git rebase --onto origin/main 10996616`: `ba852261` ->
  **`4537961b`** (`695bd4c2`, `4537961b`), pushed with `--force-with-lease`. No conflict; `integrations/vllm` at `4537961b`
  is identical to `ba852261`, and main == a4 inside `integrations/vllm`. Main's other 52 files are outside it
  (backends, benchmarks, `tools/research` notes.py + an opt-in `refresh --payloads` in store/local.py, cli.py).
- 14:24Z laptop re-check of the split (`tools/verify_split.py`): 84/84 statements verbatim; fp8/collectives differ only in
  import lines.

## Pods (inherited)
- `vyv-rf-b5pat-cpu` = RunPod `andiw61o3shls8` (cpu3g 16 vCPU / 64 GB, $0.64/h), created ~12:10Z. Idle since 13:31Z.
- `vyv-rf-b5pat-big` = RunPod `8n2373g922sb59` (cpu3m 32 vCPU / 256 GB, $1.76/h), created 12:13Z.
  - Gate (a) at head: run `r20260925-122214-cc3f` (gate_a.sh, `--no-sampler`), started 12:22Z, 45 % at 14:15Z.
    Logs `/workspace/b5pat/logs/a_head.{log,xml}`.
  - 14:17Z #101 re-fold at head and base: run `r20260925-141717-7caf` (`--custody-r2`, `/workspace/b5patb/refold_chain.sh`,
    profile `derived_LLAMA32_1B`), out `/workspace/b5patb/refold/`.

- 14:26Z cpu pod: lints + gate (b) at the rebased head `4537961b`: run `r20260925-142622-edbe` (`--custody-r2`), tags
  `lints_rb`, `b_rb`; jdiff vs `b_head` and `b_base` into `/workspace/b5patb/jdiff_rb_vs_{head,base}.txt`.

## Next
- `r20260925-142622-edbe` result (~15:00Z); then drain the cpu pod.
- Gate (a) at `ba852261` (~16:15Z est.): compare with a23b's same-pod base XML test by test; drain the big pod.
  It carries to `4537961b` (identical `integrations/vllm` and `packages/`; main's `tools/research` change is opt-in).
- READY.md.

## Open questions
- (none)

## Found, not fixed
- `properties/protected.py:38` (b2v's) still lists `verity_vllm/observe/fold/patterns.py`; `verity_vllm/*` in the same
  tuple already covers the package, so nothing changes. Left for b2v.
- Prose naming the old files (a4's rule: bare file names are not rewritten): `resolver.py:181`, `census.py:31,53`,
  `patterns_prefix.py:3`, `registry/quarantine/collective/__init__.py:14`, `engine/profiles/generic.py:15`.
