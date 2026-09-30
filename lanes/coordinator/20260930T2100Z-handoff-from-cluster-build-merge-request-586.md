---
id: 20260930T2100Z-handoff-from-cluster-build-merge-request-586
campaign: verity
lane: coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: cluster-build (bc-c2e4c12a), for infra (bc-17cc41f1)
---

# Merge request: [#586](https://github.com/danielreuter/verity/pull/586) `tools/cluster` at `640c6d76c`. Please record a `check` of that commit

- **What it is:** a new stdlib-only workspace member `tools/cluster`, the one scheduler for vy-nebius-1 and vy-nebius-2. It has:
  - the machines' description;
  - the pure planner;
  - the hash-chained ledger;
  - node 2's adapter (`nebius2`), the shadow and the node agent;
  - node 1's read-only Kueue adapter (`nebius1`, kueue-fold's, merged in).

  Its shadow runs read-only on node 2 as run `r20260930-195806-59f3`, from `d09ad49a`; nothing it decides is carried out.
- **Outside `tools/cluster`:** the root `pyproject.toml` (a new member and dependency), `uv.lock`,
  `tools/research/tests/test_pythonpath.py` (the new source root), and a line each in `AGENTS.md` and `README.md`.
- **No circuit changed**, so there is no circuit-check report. Nothing is under `backends/flock/`, so `lean-agreement` doesn't
  apply.
- **Clean on main:** I merged `origin/main` at 20:23Z (`b8f695e16`).
- **Local `suites.py --quick` at `b8f695e16`:** every suite passes, `cluster` with 92 tests, except one `integrations_vllm` test:
  `test_tp_moe_members[...tp2...]`. Its build subprocess died under this VM's 5.3 GiB memory budget. #586 doesn't touch
  `integrations/vllm`, so a pod `check` should pass it.
- **PR description:** #586's description predates the adapter, shadow and agent. I have no pull-request tool, so please update it
  from this note, or ask me for the text.
- **Separate, not in this request:** gpu-lease's agent mode is on `cursor/gpu-lease-agent-mode-0381`, off `infra/nebius`. It is
  the steward's to merge there (note:20260930T2050Z-handoff-from-cluster-build-gpu-lease-agent-mode).
