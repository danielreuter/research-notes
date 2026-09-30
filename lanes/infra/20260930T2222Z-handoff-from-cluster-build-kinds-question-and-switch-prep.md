---
id: 20260930T2222Z-handoff-from-cluster-build-kinds-question-and-switch-prep
campaign: verity
lane: infra
kind: handoff
status: open
repo: danielreuter/verity
origin: cluster-build (bc-c2e4c12a); replies to note:20260930T2155Z-handoff-from-infra-kind-question-field, note:20260930T2158Z-handoff-from-infra-refuse-gpus-without-queue, note:20260930T2213Z-handoff-from-infra-switch-timing-window-plan
---

# cluster-build -> infra, 3:22 PM PDT: kinds, `--question` and the flag refusal are on a follow-up branch; the switch is prepared and on hold

- **Follow-up branch** `cursor/queue-kinds-0381` (`05363da79`), stacked on `--queue`. I'll rebase it onto `main` when TQS lands
  and send the merge request then.
  - **The kind registry,** `tools/cluster/kinds/<owner>.toml`, read from the shipped tree and recorded with its sha256.
    A kind supplies the job's shape, time and question; the held rules warn and never refuse.
  - **`--question`:** it defaults to the kind's and is recorded in the run record. A job with no question gets a warning.
  - **The kind in the lease holder** (`who=<kind>:<submitter>`), for node2-ops' monitors.
  - **The refusal:** `--gpus`, `--cpus` and the other queue flags are refused without `--queue`.
  - **The seed:** proofs' `lean-audit`, with a placeholder question I've asked proofs to confirm.
- **Not tonight:**
  - the brain's ledger doesn't see queued CPU jobs, so the question isn't in the ledger yet;
  - `cluster usage --by question`, `--by kind` and `--by lane`.
  Both need queued jobs in the ledger, which comes with the agent's live mode and the T4 work.
- **The switch** is ready: `note:20260930T2217Z-handoff-from-cluster-build-switch-prep`, on hold for Daniel's yes.
  - `infra/nebius` can fast-forward to `e529dc4ac` (agent mode and `fill_runner`, merged with today's branch).
  - The live agent launches from TQS's merge.
  - The live shadow at 2 h 17 min: 0 safety divergences. It left window 6 and a 2:02 PM window alone.
- **This VM was reset at about 3:10 PM PDT.** Everything was already on origin; the notes clone and SSH access are rebuilt.
