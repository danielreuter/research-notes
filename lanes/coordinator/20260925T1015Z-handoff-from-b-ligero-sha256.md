# handoff: MALLOC default, merge-ready (reply to 10:03Z)

**Commit:** `98d878ca` on `lane/b-ligero-sha256`, pushed. It is a single commit touching 3 files, and its parent has those 3 files byte-identical to main `3301c435`, so `git cherry-pick 98d878ca` onto main applies with no conflict. You don't need to merge the rest of the lane.

1. **`backends/direct/ligero/pod_bootstrap.sh`:** the env.sh heredoc now exports `MALLOC_MMAP_MAX_=${MALLOC_MMAP_MAX_:-0} MALLOC_TRIM_THRESHOLD_=${MALLOC_TRIM_THRESHOLD_:-1000000000000}`. The `${…:-}` defaults are escaped, so they stay literal in env.sh and a lane can still override either one.
2. **`verity_numerical/bench/contract.py`:** adds `allocator_env()` and `ALLOCATOR_ENV`.
   - `contract.fingerprint()` now always writes `software.allocator = {"MALLOC_MMAP_MAX_": <value|"unset">, "MALLOC_TRIM_THRESHOLD_": <value|"unset">}`, unless the caller passed its own.
   - Every bench that builds its fingerprint through `contract.fingerprint` (relchain.py, vu.py, run.py, fp4, ligerito, the gkr and vector runs) gets the field with no call-site change. `bench_result.py` passes `software` through.
   - The field is not an identity field, so `incomparable()` is unchanged and old results stay comparable. Results recorded before this commit carry no `software.allocator` field; read that as unknown, most likely unset.
3. **Tests (`test_bench_contract.py`):**
   - `test_fingerprint_records_the_malloc_tunables`: covers unset, set, and caller-given values.
   - `test_pod_env_sets_the_malloc_tunables`: checks that the env.sh heredoc carries both exports.
   - Results: the bench suite gives 257 passed and 5 skipped with the worktree on PYTHONPATH. The heredoc was checked by hand: sourcing the written env.sh under `env -i` gives `0 1000000000000`.

Caveat: glibc reads these variables at process start. A `.py` driver that sets them via `os.environ` has no effect on itself, so they must be exported in the shell, which env.sh does.
