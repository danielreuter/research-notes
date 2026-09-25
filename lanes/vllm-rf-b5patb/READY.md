---
id: vllm-rf-b5patb/ready
lane: vllm-rf-b5patb
kind: ready
status: DRAFT (gate (a) and the rebased gate (b) running)
created: 2026-09-25T14:32Z
---
# vllm-rf-b5patb READY: split the fold's kernel-pattern module into `observe/fold/patterns/` (B5)

Successor of b5pat (bc-c87a1519, hung at 12:30Z). Start commit `ba852261`; the code commits are the predecessor's.

- **Branch:** `lane/vllm-rf-b5patb`
- **Head:** `4537961b`, two commits on main `33e4d8d1` (a4 merged): `695bd4c2` (the split) and `4537961b` (fp8 and
  collectives join the package). These are `ff7a0f8c` and `ba852261` rebased with `git rebase --onto origin/main 10996616`.
  There were no conflicts, and `integrations/vllm` at `4537961b` is byte-identical to `ba852261`.
- **Base:** `10996616` (a4's head) for the gates run before the rebase. Main `33e4d8d1` is identical to it inside
  `integrations/vllm` and `packages/`.

**Summary:** a pure structural split. The fold digest of #101 re-folded at head equals the base and the record
(`cc48449d…`), with the Program and instances byte-identical. Gate (b) has no outcome change on 4,001 tests. Lints are
green. Gate (a): TBD.

## What changed
- `observe/fold/patterns.py` (1,903 lines) becomes `observe/fold/patterns/`:
  - Shared helpers: `resolutions`, `ops`, `geometry`, `transparent`, `target`.
  - Families: `gemm`, `norms`, `rotary`, `kv_cache`, `attention`, `activations`, `embedding`, `sampling` (582 lines, the
    largest).
  - All 84 top-level statements moved verbatim, with the same source lines and AST, checked on the laptop at head with
    `tools/verify_split.py`. Only the six section banners were dropped.
- `observe/fold/patterns_fp8.py` becomes `patterns/fp8.py`, and `observe/fold/collective_pattern.py` becomes
  `patterns/collectives.py` (git mv). Only their import lines changed; they now import from the sibling modules.
- `patterns/__init__.py` re-exports exactly the 56 names callers import from `verity_vllm.observe.fold.patterns`,
  including the resolver's `PerRow` and `Shared`. There is no `__all__`, because string literals would be P8
  layer-class facts. The package imports `registry.b1` eagerly, as before. `fp8` and `collectives` aren't imported by
  `__init__`, so importing the package doesn't load `registry.fp8` or `registry.b1_tp2`.
- Importers of the two moved files: `engine/profiles/generic.py`, the lazy import in `vllm_d9105ea80_sm89_eager.py`, and
  4 tests (`test_tp2_d90_fixture`, `test_gen_ov_moe_qwen3`, `test_profiles_generic`, `test_fp8_profile`), import lines
  only. The `integrations/vllm/README.md` observe/ line was also updated.
- Match order: the profiles' pattern lists and the resolver's first-match loop are untouched. #101's
  `fold.report.by_pattern` has the same 13 patterns and 17,199 matches, in the same order, at head, base and in the record.
- Allowlists (base -> head, entries / violation totals):
  - p10: 76 -> 75. The `patterns.py` `<module>` entry (1,903) is deleted, and the total drops by exactly 1,903.
  - p08: 300 / 399 = 300 / 399. p09: 177 / 183 = 177 / 183. p11: 715 / 966 = 715 / 966. Their entries moved with the code
    (P8 1, P9 2, P11 7 + 3).
  - Every other allowlist is unchanged. No allowlist grew.

## What deliberately didn't change
- Callers keep importing from `verity_vllm.observe.fold.patterns`: the package surface replaces the module, so no other
  lane's file changed for the split itself.
- Every pattern class, name, pin and reason string, and every profile module's pattern list.
- Prose that names the old files (see "Found, not fixed").

## Gate evidence
Pods, both inherited from b5pat:
- `vyv-rf-b5pat-cpu` = RunPod `andiw61o3shls8`: cpu3g, 16 vCPU / 64 GB, $0.64/h. It ran lints, gate (b) and the code
  identities.
- `vyv-rf-b5pat-big` = RunPod `8n2373g922sb59`: cpu3m, 32 vCPU / 256 GB, EPYC 7702P host, $1.76/h. It ran the prefetch,
  gate (a) and the re-fold.

Environment: `pod_bootstrap.sh --cpu` + `pytest-xdist==3.8.0`, with `xgrammar 0.2.7`, `googleapis-common-protos 1.75.3`
and `uvicorn 0.53.0` pinned (run `r20260925-120859-*` on each pod). The trees were shipped by `research run --source`:
`/workspace/research/src/{ba852261…,10996616…,4537961b…}`. Gate (b) ran on copies (`/workspace/trees/TAG`).

### Lints
`python -m pytest integrations/vllm/tests/lint integrations/vllm/tests/test_no_by_name_rules.py
integrations/vllm/tests/test_imports_resolve.py -q` (`tools/lints.sh`), cpu pod, run `r20260925-122258-1b8d`:
- head `ba852261`: rc 0, 45 passed. Base `10996616`: rc 0, 45 passed.
- Rebased head `4537961b`: run `r20260925-142622-edbe`, TBD.
- Evidence: `evidence/lints_{head,base}.xml.gz`.

### (b) `OMP_NUM_THREADS=3 python -m pytest integrations/vllm/tests -ra -n 12 --dist loadfile`
Same pod, one after the other (`tools/gate_b.sh`), run `r20260925-122258-1b8d`:
- head `ba852261` 12:24-12:57Z and base `10996616` 12:57-13:31Z: both 4,001 tests, with 3,647 passed, 51 failed,
  11 errors, 286 skipped and 6 xfailed.
- a1's `baseline-jdiff.py`, base -> head: 0 only-in-base, 0 only-in-head, 0 outcome changes, 0 new failures, 0 new skips,
  0 new skip reasons, rc 0. No test was renamed.
- Fold and pattern test modules: 207 passed, 1 failed and 5 skipped on both sides. The failure,
  `test_patterns_synthetic::test_gumbel_two_stage_sampler_is_one_token_select`, is identical at base (see "Found, not
  fixed").
- Rebased head `4537961b`: run `r20260925-142622-edbe`, TBD.
- Evidence: `evidence/b_{head,base}.xml.gz`, `evidence/jdiff_b.txt`.

### (a) `VERITY_REGRESSION=1 VERITY_REGRESSION_TIERS=T0,T1 python -m pytest integrations/vllm/tests/regression -m regression`
- Big pod, head `ba852261`, run `r20260925-122214-cc3f` (`tools/gate_a.sh`, `--no-sampler`), from 12:22Z: TBD.
- Fixtures: a laptop-minted read-only key fetched all 26 artifacts (26 ok, 0 FAIL), and the key was deleted at
  12:21:25Z. The run's status line reads `key_file_present=no`.
- Why it holds for `4537961b`: `integrations/vllm` and `packages/` are identical. Main's `tools/research` change adds
  an opt-in `refresh --payloads` path and notes tooling, and gate (a)'s local-store fixture path doesn't call either.

### Lane acceptance: re-folded record Programs byte-identical
Row #101 is the only fixture row whose capture log is in the fixtures. Its record
(`art:a4ea1a18…/match/capture/log.jsonl.gz`) was re-folded at head and base on the big pod, run `r20260925-141717-7caf`
(`tools/refold_chain.sh`, `--custody-r2`). It ran the Match `fold` worker with `--persist-dir`, then `resolve_log`, as
`pipeline/match.py`'s Plan builds them.
- **Profile:** the record names `gen_llama_llama32_1b`, a module that P6 removed. The role's profile today is
  `derived_LLAMA32_1B`, which is what `profile_module_for_case("LLAMA32_1B")`, `run_config` and `stoch_negatives.sh` pick.
  b5pat's first re-fold (`r20260925-122818-9e8a`) used the old name and failed at import on both sides.
- **Fold digest:** `cc48449d534f7e10…` at head, at base and in the record.
- **Byte-identical, head vs base:**
  - `program.json`: sha256 `ef5b2fe5…`, 17,119,764 B.
  - `instances.jsonl`: `3743f58c…`, 60,986,770 B.
  - `resolution.md`.
- **Content-identical:** `accesses.jsonl.gz`, whose gzip header mtime is the only difference; it decompresses to the
  same 69,010,040 bytes.
- `fold_summary.json` and `resolution.json`, head vs base, differ only in `utc`, `seconds`, `*_s` timings, `max_rss_gb`
  and output paths (`tools/deep_diff.py`).
- **Against the record:** the digest and by_pattern are equal. The persisted byte sizes and the resolution's
  `spec_modules` differ at base and head alike, because the record predates the `progressions` operand form and a4's
  registry moves.
- Evidence: `evidence/refold-r101.txt`, `evidence/refold-r101-deepdiff.txt`.

## Code identities (before -> after; allowed to change)
Computed on the cpu pod with a4's `tools/ident.py` (`evidence/ident-{10996616,ba852261}.json`):

| identity | base `10996616` | head `ba852261` |
|---|---|---|
| `code_identity` = hot-commit key = research Tools closure (VLLM_BUILD/MATCH/COMMIT) | `3809d208…` (1,169 files) | `e82dbc8b…` (1,182 files: -1 `patterns.py`, +14 package files) |
| `construction_version.sources_sha256` | unchanged | unchanged |
| `registry_version.digest` | unchanged | unchanged |

No Program digest, manifest digest, commitment root, leaf id or regression verdict changes. There is no epoch commit.

## Found, not fixed
- `properties/protected.py:38` (b2v's) still lists `verity_vllm/observe/fold/patterns.py`. `verity_vllm/*` in the same
  tuple already covers the package, so nothing changes.
- Prose that names the old files (a4's rule: bare file names aren't rewritten): `resolver.py:181`, `census.py:31,53`,
  `patterns_prefix.py:3`, `registry/quarantine/collective/__init__.py:14`, `engine/profiles/generic.py:15`.
- Recorded `match/run.json` and `fold_summary.json` name pre-P6 profile modules (for example `gen_llama_llama32_1b`),
  which no longer import. Any tool that re-folds a record by its recorded profile name has to map it to
  `derived_<ROLE>` first.
- These fail identically at base and head: `test_patterns_synthetic::test_gumbel_two_stage_sampler_is_one_token_select`
  (the sampler logits width is not the vocabulary) and `test_gen_sampling::
  test_load_workload_honours_sampling_block_and_keeps_greedy_default` (`NameError: execution_of_workload`). They are
  among gate (b)'s 62 pre-existing failures and errors.

## Spend
TBD
