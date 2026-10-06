---
id: red-team-vbridge-b/20261006T0405Z-friction-cwd-clone-pythonpath
campaign: proofs
lane: red-team-vbridge-b
kind: friction
status: open
repo: verity
origin: run:r20261006-025421-cbce
---

# `research run --cwd clone` imports Python from the shared source tree, not the run's clone

`audit.py --build verity/Security` at `7c5cb816e` on vy-nebius-1 with `--cwd clone` (r20261006-025421-cbce, 45 min)
passed every Lean check, but failed `verity/Security/Proofs` on one `runs` test. The `generate` step of
`Proofs.Warden.DifftestMain` (`warden/lean/scripts/difftest_vectors.py`) refuses when `verity.protocols.accounting.communication.warden`
is imported from outside the checkout it audits. The workload ran in `scratch/<run>/tree`, but `remote._runner_env` builds
`PYTHONPATH` (the `pyshim` for `verity`) from `src_dir` (`src/<sha>`) whether or not `--cwd clone` is set, so `verity` came
from `src/<sha>`. That tree has the same verified commit, but sits on a different path. Cost: one failed audit attempt and a rerun.

Workaround: `bash -c 'd=$(mktemp -d); trap "rm -rf $d" EXIT; ln -s "$PWD/verity" "$d/verity"; PYTHONPATH="$d:$PYTHONPATH" python3 tools/lean/audit.py ...'`
(r20261006-040139-db49, PASS). The better fix is for `_runner_env`, under `--cwd clone`, to build `PYTHONPATH` and the shim
from the clone root, so a run's imports and its cwd are the same tree. Until then, every audit of `verity/Security`
recorded with `--cwd clone` fails this `runs` test.
