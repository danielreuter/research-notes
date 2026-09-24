---
lane: bench-summary
kind: report
created: 2026-09-24T00:45Z
status: final
---
CHECKPOINT fd2971e8 (00:58Z) [final] FINAL written below. Tip fd2971e8, worktree clean, no pod. Robustness: all of ~/.research/runs (1516 runs -> 691 rows, 2.1 s wall) and ~/.research/store/manifests (4048 manifests -> 539 rows, 1.1 s) summarise with no crash and no stderr.
CHECKPOINT fd2971e8 (00:55Z) [open] summary.py + tests/bench/test_summary.py committed; 4 new tests pass (0.15 s), bench suite 162 passed / 5 skipped (test_instances: built operand arrays absent, pre-existing), ~9 s CPU. Real-data smoke runs OK (nested run dir, flat v3-scout-2, repo ligero results, store manifest). Found on the way: r20260923-223427-9bab p4/bench/bare fails the contract (buckets sum 2.2 % over t.total).
CHECKPOINT 22e10e0e (00:50Z) [open] worktree + branch lane/bench-summary created from main@22e10e0e; read tables.py (_measurements, phases, _mode_of, normalise_sku, _md_table), contract.py, lane summ.py/table.py scripts (v3-scout, v3-scout-2, open-fixes, hints-fused-2), real run dirs (~/.research/runs/*/bench/*/result.json + rust_batch.json) and store manifests (bench-result/v1 = {kind, meta: result}). All 539 store results have list measurements. `import verity_numerical.bench.tables` pulls no third-party module. Writing summary.py next.

# bench-summary: one bench-result summary helper (workflow-review R4)

Goal: `python -m verity_numerical.bench.summary PATH... [--cols ...] [--md | --json] [--sort COL]` replaces the ~15 per-lane
`summ.py` / `table.py` scripts. Stdlib only; reuses `tables._measurements` / `tables.phases` (the frozen bucket identity).

## Layouts seen in real data (what discovery must handle)

- `<run>/bench/<variant>/result.json` + `rust_batch.json` beside it (`~/.research/runs/r20260923-211722-820d`), up to three
  levels below the run (`r20260923-223427-9bab/p4/bench/bare/result.json`).
- `<run>/result.json` + `proofs/rust_batch.json` (blake3-leaf `table.py`).
- flat `<tag>.json` + `<tag>_rust.json` (v3-scout, v3-scout-2 `evidence/results/h100/`).
- store manifests `~/.research/store/manifests/<id>.json` of kind `bench-result/v1` (the result is `meta`).

## FINAL

tip: lane/bench-summary @ fd2971e8 (base main@22e10e0e)
merge-with: none
known-failures: none (bench suite 162 passed, 5 skipped: `test_instances` needs the locally built operand arrays; pre-existing, environment-only)
pod: none

Usage example on a real run dir (lane fp8-ada / bf16-hopper benches on an RTX 4090, `rust_batch.json` beside each `result.json`):

~~~text
$ python -m verity_numerical.bench.summary ~/.research/runs/r20260923-223427-9bab --sort t.total
label               relation       gpu   VUs  N_sub      l  pipe   zk         mode  t.total     wit     enc   arith  lookup  zk_add     ser    other  dev_GiB  proof_MB  validation   contract          rust      bound
p4/bench/bare        fp8-ada  rtx-4090  4096     13  16384     4  yes  interactive   0.2153  0.0177  0.0532  0.1278  0.0000  0.0002  0.0211  -0.0047     6.12      66.1      passed  1 problem  ACCEPT 13/13  2^-128.32
p3/bench/bare        fp8-ada  rtx-4090  4096     13  16384     3  yes  interactive   0.2204  0.0138  0.0549  0.1255  0.0000  0.0004  0.0251   0.0007     4.74      66.1      passed         ok  ACCEPT 13/13  2^-128.32
p4/bench/hbare   bf16-hopper  rtx-4090  4096     25  16384     4  yes  interactive   0.2798  0.0218  0.0726  0.1618  0.0000  0.0001  0.0255  -0.0022     5.15     118.0      passed         ok  ACCEPT 25/25  2^-128.05
p3/bench/hbare   bf16-hopper  rtx-4090  4096     25  16384     3  yes  interactive   0.3292  0.0129  0.0792  0.2000  0.0000  0.0006  0.0363   0.0002     4.00     118.0      passed         ok  ACCEPT 25/25  2^-128.05
p4/bench/ajtai       fp8-ada  rtx-4090  4096     13  16384     4  yes  interactive   0.4469  0.0927  0.0537  0.2826  0.0000  0.0000  0.0198  -0.0018    10.76      77.2      passed         ok  ACCEPT 13/13  2^-128.32
p4/bench/hash        fp8-ada  rtx-4090  4096     13  16384     4  yes  interactive   0.4484  0.0757  0.0859  0.2674  0.0000  0.0000  0.0217  -0.0024    10.19      90.9      passed         ok  ACCEPT 13/13  2^-128.32
p3/bench/hash        fp8-ada  rtx-4090  4096     13  16384     3  yes  interactive   0.4719  0.0617  0.1087  0.2777  0.0000  0.0001  0.0237  -0.0000    10.19      90.9      passed         ok  ACCEPT 13/13  2^-128.32
p3/bench/hhash   bf16-hopper  rtx-4090  4096     25  16384     3  yes  interactive   0.8231  0.1194  0.1463  0.5116  0.0000  0.0001  0.0421   0.0037     9.77     164.2      passed         ok  ACCEPT 25/25  2^-128.05
p4/bench/hhash   bf16-hopper  rtx-4090  4096     25  16384     4  yes  interactive   0.8359  0.1273  0.1605  0.5026  0.0000  0.0001  0.0454   0.0000     9.77     164.2      passed         ok  ACCEPT 25/25  2^-128.05
p3/bench/hajtai  bf16-hopper  rtx-4090  4096     25  16384     3  yes  interactive   1.4071  0.2812  0.1389  0.9151  0.0000  0.0001  0.0615   0.0102    13.11     145.2      passed         ok  ACCEPT 25/25  2^-128.05
~~~

`--json` of the flagged row gives the reason: `contract_problems: ["buckets and joints sum to 0.220024 s, more than t.total
0.215307 s by over 1%: something is double-counted"]` -- the canonical tables would reject that result on its contract.

### What landed (1 commit on main@22e10e0e)

- `backends/numerical/python/verity_numerical/bench/summary.py` (188 lines, 138 of code without docstrings/blanks; a bit
  over the ~120 target, mostly the row dict and the CLI's error handling). Thin layer over `tables._measurements`,
  `tables.phases` (buckets, joints and `other` exactly as Table 3 computes them; a joint prints in its first bucket and
  `tables.JOINT_CONTINUATION` in the others, with a one-line legend), `tables._mode_of`, `tables.normalise_sku`,
  `tables._md_table`, `contract.validate` and `contract._lookup`. No bucket logic of its own. Imports nothing outside the
  stdlib and the repo's `verity` / `verity_numerical` (`research` only through tables' existing optional import); the pod
  bootstrap's `uv sync` provides both.
- `backends/numerical/tests/bench/test_summary.py`: 4 tests, 0.15 s, synthetic `result.json` / `rust_batch.json` fixtures
  in `tmp_path` built from the conftest's `conforming_result()`:
  phase identity reuse (incl. a joint), discovery over all four layouts (and `proofs/` pruned, non-results skipped),
  `--cols` / `--sort` / text / markdown rendering (empty columns dropped), and problems reported without being fatal (a
  contract problem, a malformed joint that makes `tables.phases` raise, empty input -> exit 1).

### Row contents

`label` (path relative to the common parent of the PATH args, minus `result.json` / `.json`), `relation` (from
`software.backend.name`: "b-ligero chain, fp8-ada relation (...)" -> `fp8-ada`), `gpu` (normalised SKU), `VUs`, `N_sub`,
`l` (`security.rs_l`), `pipe` (`software.backend.pipeline`), `zk`, `mode`, `t.total`, `t.total_live`, the six buckets +
`other`, `dev_GiB` / `host_GiB` (peak), `proof_MB` (`transcript.bytes`, else `proof_bytes` / `proof.bytes_total`),
`validation` (the result's own status), `contract` (`ok` / N problems), `rust` (`ACCEPT 13/13`, plus `UNPINNED` /
`py-disagree=N` when so) and `bound` (the batch union bound, `2^-128.32`). `--cols` takes measurement names, else dotted
paths into the fingerprint or the result (`--cols threads,lookup_mode,proof_class` works for GKR rows). A column empty in
every row is not printed. `--json` adds `path`, `run_id`, the full `phases`, `contract_problems` and `rust_file`.

### For the coordinator

- Suggested LANE-CONTRACT §8 line: "Summaries: `python -m verity_numerical.bench.summary <run dir>... [--md]`; no per-lane
  summ.py." I did not edit `backends/AGENTS.md` (the helper is not a table of record, and a shared doc invites conflicts).
- Not built on purpose: aggregation over repeated rounds (v3-scout-2 `table.py` median/min/max over `TAG`, `TAGr2`, ...).
  It is one row per result by design; `--json` plus a few lines covers it if it recurs.
- Store-wide, 223 of the 539 `bench-result/v1` results fail `contract.validate` (mostly older runs). This is a read-out
  of `summary ~/.research/store/manifests --json`, not something I investigated further.
