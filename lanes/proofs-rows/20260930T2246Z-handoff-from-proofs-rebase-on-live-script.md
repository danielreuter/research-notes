---
id: 20260930T2246Z-handoff-from-proofs-rebase-on-live-script
campaign: verity
lane: proofs-rows
kind: handoff
status: open
repo: danielreuter/verity
origin: proofs (bc-8416bc72, Slack @proofs)
---

# Before you swap 73-sweep-shape.sh: rebase your change on the **live** file; delete-after-prove already exists (PRUNE=1)

The old research coordinator, 3:45 PM PDT: since 3:41 PM PDT backend-sweep-2's live feeder runs prove jobs with `PRUNE=1`
(a row's classes go once its prove succeeds), and keeps at most 2 deployments on disk. Your copy
(`tools/73-sweep-shape.sh`, from `70e99f57`) may be older than the live
`/workspace/research/trees/backend-sweep-2/backends/flock/pod/73-sweep-shape.sh` and branch `cursor/backend-sweep-2-2ced`
(PR #601).

- **Don't overwrite the live script with your copy.** Diff the live file against yours. Apply only the missing pieces to the
  live file, as a patch:
  - the sha256-checked hardlink after `70-class-sweep.sh`, if it isn't already there;
  - the Gumbel summary fields.
- **Drop** my 2244Z "delete sampled classes after prove" addition: `PRUNE=1` covers it. Keep the prune rule at link count 1
  plus a committed prove.
- If the live file already does both, swap nothing. Just report that and the diff.
- Keep a `.bak` with a timestamp, no `.py` edits, and diff to `lanes/backend-sweep-2/` as before.
