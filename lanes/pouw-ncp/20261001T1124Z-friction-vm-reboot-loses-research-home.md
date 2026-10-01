---
id: pouw-ncp/20261001T1124Z-friction-vm-reboot-loses-research-home
lane: pouw-ncp
kind: friction
status: open
---

# An agent VM reboot drops `~/.research` and `/tmp`, so `research fetch` no longer knows the runs it launched

At 11:12Z this cloud VM rebooted from its snapshot (uptime 0). Three things were lost: `~/.research` (the notes clone, run records, `lane-env.sh`), `/tmp`, and the parent Project store's mount. The checkout was also left on another agent's branch. The timed run r20261001-104904-38fa, launched at 10:49Z, was unaffected on node 2.

Restoring cost about 10 minutes:
- `research fetch <run>` refuses ("no run matching ... under ~/.research/runs"). I copy the run dir with `research pods ssh vy-nebius-2 -- tar -C /workspace/research/runs -cz <run>`.
- The global `url.*.insteadof https://github.com/` rewrites the notes remote to the cursor bot's token, so the push gets a 403. I set the remote to `https://x-access-token@github.com/danielreuter/research-notes`, with a local credential helper that reads `$RESEARCH_NOTES_TOKEN`.

Better: let `research fetch <run> --on MACHINE` fetch from the machine's `root` without a local record, and have one `research bootstrap` recreate `~/.research` from the env.
