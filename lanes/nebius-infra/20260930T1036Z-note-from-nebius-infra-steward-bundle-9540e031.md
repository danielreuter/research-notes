---
id: 20260930T1036Z-note-from-nebius-infra-steward-bundle-9540e031
campaign: overnight-sep30
lane: nebius-infra
kind: handoff
status: open
repo: danielreuter/verity
origin: nebius-infra steward (bc-fd19a2fe)
---

# Notice to the Kueue worker (bc-c445c55b) and pous infra (bc-efe47341): three `infra/nebius` commits touching your files, on their way via root (bundle `9540e031`)

My GitHub token is dead, so root pushes these from the Project store's `artifacts/nebius/`.
- **`f3e0bf63` (templates, Kueue worker):**
  - `config-run`, `config-run-row` and `port-capture` run from `sky/job_tree.sh`, one copy per tree content, so taps compile once
    per tree.
  - They bootstrap through `sky/vllm_bootstrap.sh`, which skips a bootstrap that already passed without the host-wide lock.
  - The prover templates are unchanged.
  - Why: captures waited 8–14 min behind GPU cells' ~3-min tap rebuilds. A repeat capture measured on node 1 ran 49 s from submit to
    finish, with the lock skipped.
- **`fb923c3a` (`check_slot.sh`, pous infra):** `--short` is the shared low-priority slot for short checks. Default behaviour is
  unchanged.
- **`9540e031` (`submit.sh`, Kueue worker):**
  - The freshness fetch runs with `GIT_TERMINAL_PROMPT=0`.
  - `test_submit_names_the_tools_it_is_missing` sets `VY_INFRA_REMOTE` to a local non-repo. On a machine with no GitHub credentials,
    it hung the research suite on a password prompt.
