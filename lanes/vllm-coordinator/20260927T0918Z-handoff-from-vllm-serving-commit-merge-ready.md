---
cursor:
  subagentId: "bc-819f6247-2b10-5a85-9352-4e1d932f2125"
---

lane: vllm-coordinator · kind: handoff · from: vllm-serving-commit (bc-819f6247) · created: 2026-09-27T09:18Z

# MERGE-READY: PR #119, `lane/vllm-serving-commit` @ `5581920f`, base main `928790af`

[PR #119](https://github.com/danielreuter/verity/pull/119): opt-in serving rows. vLLM commits every RoPE head of a run in M0's serving
row format (`frame-v3-sha512` rows, `hm96-sha512/v1` leaves, SHA-512 roots), with the registration, unit index and M0's public and
prover files the one-stage audit reads. `vllm-v1` stays the default and the record.

## Gates

- **Gate (b)** (`gate_b2.sh` in git clones on one pod, `vyv-rf-serving-commit-cpu`):

  | side | run | record | lints | suite |
  |---|---|---|---|---|
  | base `928790af` | `r20260927-074901-3cb9` | `art:5011e1db…` | rc 0 | 4,052 passed, 34 failed, 286 skipped, 6 xfailed, 11 errors |
  | head `5581920f` | `r20260927-081242-9c58` | `art:133e0286…` | rc 0 | 4,061 passed, 35 failed, 286 skipped, 6 xfailed, 11 errors |

- **jdiff** (`baseline-jdiff.py`, rc 0):
  - nothing deleted or renamed;
  - **10 new tests**, all passing: `tests/commit/test_serving_rows.py`;
  - **1 outcome change**, `tests/commit/test_roundtrip::test_transient_storage_is_released`, passed → failed:
    - it measured 40,074 B of `tracemalloc` growth across a commit against a bound of 37,984 B, about 2 KB over;
    - it **passes alone on head**, and **after `test_serving_rows.py` in the same process**, on the VM at `5581920f`;
    - the test sums allocation growth over every file inside its window, so a first-time lazy import or cache in the same worker
      counts against it;
    - adding a test file changes which files share an xdist worker under `--dist loadfile`;
    - so it's order-dependent, not a regression, and it's listed under found-not-fixed.
  - Nothing else changed: 0 new skips, 0 fixed, and the base failures are main's own.
- **Lints:** P7, P9, P10 and P11 failed on the first head (`993ea8ff`) and are fixed in `5581920f` with no allowlist growth (see
  "Behaviour"). The only allowlist edit **lowers** `commit.py main`'s P10 cap from 1770 to 1769.
- **Partition invariants:** no change here adds or restates a Definition, query or partition. The code consumes the verifier's
  partition file (`Q_template_instance` v0, the e2e lane's and core's), so the partition checker doesn't apply.

## Default path (scheme off)

- **CPU:** `verity-vllm manifest build` over the stored #101 Build `art:9cb3a4df` gives `90f81868…` on main and on the branch, with
  byte-identical files (sha256 `9e010897…`).
- **GPU:** #101, scheme off (`r20260927-061338-8809`, `art:4474915c`): verdict PASS, program `ccc21347`, manifest `90f81868`, run root
  `7adcef49`, **equal to the record**.
- **With the scheme on,** the `vllm-v1` run root stays `7adcef49` in both served runs.

## Evidence (1× L40S)

- **Pre-canonical partition `f6e07626…`:** served run `r20260927-061338-8809` (`art:4474915c`). All 183,680 heads committed, roots `x`
  `c62a5fde…`, `cs` `ee9ed668…`, `out` `de08eeab…`.
- **Byte-match** (`r20260927-065834-9db4`, `art:107b97ee`):
  - the 1,024 captured heads (`art:16825154`) are all located, and `x`, `cs`, `out` are byte-equal;
  - M0's `write()` at `e51e2b86` over all 183,680 served heads, with serving's salts and domains, gives `pub-183680.bin` and
    `inst-183680.bin` byte-identical to serving's, headers included;
  - the circuit pin is `cdcbd876…`.
- **Canonical partition `17478e85…`:** re-served in `r20260927-073101-9c1c` (`art:fa1b749f`). `7adcef49` unchanged, the byte-match
  passes again with pin `517b72e7…`, and the e2e lane's `R.check` (`761c4402`) accepts the v1 registration `7b7a1ca3…`.
- **Public bundles:** `art:fcc4e542` (pre-canonical) and `art:9ab217a1` (canonical). The e2e lane ran A2 on both, accepted and
  `complete: true`.
- **Serving overhead:**
  - time: the hook took 14.6–15.1 s (about 9.5 s reading through openings, about 5 s hashing on 16 workers), against a Commit stage
    of 190 s on and 193 s off;
  - bytes: 70.5 MB of values hashed, against about 908 MB for `vllm-v1`; 70.5 MB public and 117.6 MB private kept.

## Behaviour

- **New:**
  - `verity_vllm/commit/serving_rows.py`: the scheme, salts, domains, registration and files. It imports nothing above `commit`.
  - `verity_vllm/pipeline/serving_rows.py`: the RoPE reading, as the replay reads it, and the Commit hook.
- **Commit:** a new option `--serving-rows REQUEST_JSON`. The hook is the existing line that built the replay's weights provider and
  opened reader, and it returns the same two objects. With a request, it first commits the serving rows through its own opened
  reader, before the seed exists. A failure writes `error.txt` and changes no verdict.
- **Row stage:** `SERVING_ROWS=<partition file>` (config `serving_rows`, off by default) writes the request (directory, partition, run
  id, source) and passes it to the Commit.
- **Unchanged:** every root, manifest, digest and verdict of record; the replay and its seed; `vllm-v1`; `commit/hiding.py`.

## Found, not fixed

- **M0's `circuit.write()` is quadratic in n for the prover file:** an `np.concatenate` inside the per-instance loop, about an hour at
  n = 183,680. Reported to flock-netlist with the one-line fix. The byte-match hoisted it (same bytes).
- **`test_roundtrip::test_transient_storage_is_released`** is order-sensitive under xdist (above). A robust version would take its
  baseline after a warm-up commit.
- **The first served run's registration has `row: null`.** Fixed in `efec3ad1`; the canonical re-serve records it.

## Spend

About $2.66 in total: L40S $1.02 and $0.42, CPU gate pod $1.24. Every pod is terminated.
