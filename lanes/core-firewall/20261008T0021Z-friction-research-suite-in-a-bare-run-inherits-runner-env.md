---
id: core-firewall/20261008T0021Z-friction-research-suite-in-a-bare-run-inherits-runner-env
campaign: proof-service
lane: core-firewall
kind: friction
status: open
repo: danielreuter/verity
origin: bc-8416bc72 (proofs)
---

# The `research` suite fails one test when run as a bare `research run` job

Under the CI rule of 7 Oct (22:54Z), each suite a change touches runs as its own `research run` job. A job that calls
`suites.py research` directly gets one false failure: `tests/test_remote_cwd.py::test_two_concurrent_runs_of_one_commit_do_not_share_a_cwd`
(run r20261008-001353-1716 on vy-nebius-cpu-1, `--cwd clone`: 1897 passed, 1 failed).

Cause: the runner exports `PYTHONPYCACHEPREFIX` and `RESEARCH_*` to the workload (`cli.py`, `remote.py`). The runs the test
starts inherit them, since `remote.py` only `setdefault`s the prefix, so their bytecode goes to the outer job's cache and not
to `<root>/cache/pycache`. When `check.py` and the quick tier run suites, they strip those variables (`quick_tier.run_env`,
`RUNNER_ENV`). `suites.py` does not.

Workaround: unset them in the job, as `check` does. The re-run r20261008-001900-d2ff passed (1898 passed, 1 skipped):

~~~bash
bash -c 'unset PYTHONPYCACHEPREFIX; for v in $(compgen -e | grep "^RESEARCH_"); do unset "$v"; done;
  uv run --locked --extra torch-cpu python tools/verity/check/suites.py research'
~~~

Fix at the source (not this lane's; @infra or @ci): `suites.py` could apply `run_env`'s stripping itself when
`RESEARCH_RUN_DIR` is set, so a suite behaves the same inside a bare job as under `check`.
