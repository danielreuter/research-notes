---
id: 20260930T2128Z-handoff-from-infra-job-kinds-registry
campaign: verity
lane: cluster-build
kind: handoff
status: open
repo: danielreuter/verity
origin: infra coordinator (bc-17cc41f1)
---

# cluster-build: `research run --queue --kind K`, with a kind registry resolved from git, phase-pure kinds and fail-closed admission. Tonight's slice goes with T3

Daniel (2:14 PM PDT), after the stale node-local template: everyone requests the right resources, irregular jobs become small regular
ones, and monitoring keeps it that way. This is built into the queue, not written as a document.

**The kind registry: `tools/cluster/kinds.toml` in the repo, or `kinds/*.toml`.** It is resolved from the submitter's shipped git
commit at submit time; `research run` already ships the tree. The kind name and that commit are recorded in the ledger. There are
no node-local templates. Each kind has:
- `phase`:
  - `gpu1`, one GPU;
  - `gpu2`, two GPUs on one node;
  - `gpu8-timed`, the exclusive window;
  - `cpu-s`, `cpu-m` or `cpu-l`: CPU, memory and cores from a small menu.
- `max_wall`: GPU kinds must be preemptible and take at most 60 min. `gpu8-timed` follows the window rules.
- `inputs` and `outputs`: declared paths or store ids. Outputs are custodied before the allocation is released.
- `restart: idempotent | requeue | never`.
- `owner`: the coordinator's handle.
- `next`, optional: the kind this one hands its declared outputs to, so a Commit becomes `build (cpu-l)`, then `commit-gpu (gpu1)`,
  then `replay (cpu-m)`. The hand-off is a manifest.

**Admission. Tonight it fails closed on:**
1. an unregistered kind;
2. a GPU kind whose command has a declared CPU phase, or no `max_wall`.

**Tonight it warns and logs, and fails closed at T4, on:** a shape outside the menu; no declared outputs; a GPU kind over 60 min.
Machine money, meaning a RunPod line in `budgets.toml`, applies only to pod kinds.

**Seed kinds for tonight:** the ones the shadow and the first lane job need, e.g. `pouw-fill-gpu1`, `verity-build-cpu-l`, `check-cpu-l`.

**Per-kind efficiency:** the ledger records leased and busy GPU-seconds per job. `cluster usage --by kind` gives useful ÷ leased per
kind, and the console table and the daily top-3 list of wasters are built on it.

**Timeline:**
- **T3, tonight:** `--queue --kind` with the registry and the two fail-closed checks.
- **T4:** a kind for every workload in `lanes/infra/*workload-inventory*`. Infra seeds a draft set from the inventories, and each
  coordinator corrects its own.
- **This week:** the remaining checks go fail-closed.

Say at once if this puts T3 at risk; the registry can start as one TOML file.
