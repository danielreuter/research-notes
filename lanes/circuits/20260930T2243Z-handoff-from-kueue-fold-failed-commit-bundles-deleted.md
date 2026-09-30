---
id: 20260930T2243Z-handoff-from-kueue-fold-failed-commit-bundles-deleted
campaign: one-pool
lane: circuits
kind: handoff
status: open
repo: danielreuter/verity
origin: kueue-fold (bc-d5ffe46d)
---
# circuits (cc node1-dispatcher): a failed Commit now deletes its replay bundles, live on node 1

- **The change:** `config-run.yaml`'s Commit GPU task runs `rm -rf $SWEEP_DIR/$ROW/commit/replay_bundle_p*` on a non-zero rc, then
  exits with the same rc (86 still skips the replay). It is `infra/nebius` `aba2fce22`.
- **Deployed** at 3:38 PM PDT to node 1's dispatcher templates (backup `config-run.yaml.bak-*`). New Commit Jobs use it, and running
  ones keep their old script. The drift reference is `fc3ae8227`, and the dispatcher's `sky/` matches it.
