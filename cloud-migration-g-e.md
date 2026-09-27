---
cursor:
  subagentId: "bc-da2ec799-5aae-580c-b863-082abb94cb20"
---

# Cloud migration steps (g) and (e): PRs and switch-over

Spec: `docs/cloud-migration-requirements.md`. Siblings: `internal/cloud-migration-implementation.md` (steps c, h, d, a).

| Step | PR | Branch |
|---|---|---|
| (g) pod registry | [#7](https://github.com/danielreuter/verity/pull/7) | `cursor/pod-registry-cb20` |
| (e) liveness, lease, service | [#10](https://github.com/danielreuter/verity/pull/10) | `cursor/steward-lease-liveness-cb20` |

Both PRs are independent of each other and additive. Nothing changes on the laptop until the variables and flags below are set.

## Switch-over (after the current lanes finish; needs the notes remote from step a)

1. **(g)** On the laptop:
   `RESEARCH_MACHINES_D=~/.research/notes/machines.d research pods registry import --apply`, then `research notes sync`.
   Set `RESEARCH_MACHINES_D=~/.research/notes/machines.d` in `~/.research/bin/research` and the steward's environment.
   Cloud VMs need nothing: with no machines.toml they read `~/.research/notes/machines.d`.
   Lanes then create pods with `research pods create --name vy-<lane> ... --register --project verity`.
2. **(e)** Pick the steward host (open question 1). There, run
   `research notes service systemd --workdir <verity checkout> --env RESEARCH_REPO=<checkout> > ~/.config/systemd/user/research-steward.service`,
   then `systemctl --user enable --now research-steward.service` and `loginctl enable-linger $USER`.
   On the laptop, use `research notes service launchd` instead (the plist goes in `~/Library/LaunchAgents/`).
   Stop the old `com.research.notes-watch` job first. It holds no lease, so the two would both reap.
3. The lease key is `steward/lease.json` in the store bucket. `--lease PATH` is the single-host alternative.

## Known limits

- **Stale-pod reaping in git mode needs `--custody-r2`** (step f, merged). The service definition sets it. Without it, the local run-custody leg fails closed.
- **Steward state stays per host.** `steward-state.json` is never synced. After a takeover, expect at most one repeated RENDERED or OVERDUE line, and budget spend counted from the takeover.
- **E4 is only partly tested.** The reboot itself wasn't exercised: this VM has no systemd. The unit passes `systemd-analyze verify`.
