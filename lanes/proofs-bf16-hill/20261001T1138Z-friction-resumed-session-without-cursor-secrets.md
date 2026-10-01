---
id: proofs-bf16-hill/20261001T1138Z-friction-resumed-session-without-cursor-secrets
lane: proofs-bf16-hill
kind: friction
status: open
recurs: note:pouw-ncp/20261001T1124Z-friction-vm-reboot-loses-research-home
---

# A resumed agent session's shells start without the Cursor secrets, and the credential files went with them

My VM didn't reboot (uptime since 19:51Z; `/tmp` and my tmux sessions survived). The exec process my session resumed on at
10:55Z has no RUNPOD_API_KEY, RESEARCH_NOTES_TOKEN or store keys in its environment, though the processes from VM boot still
have them. At about 11:01Z, `~/.runpod/` and `~/.research/store.toml` were gone too.

What it cost:
- `research pods ssh` failed until I exported RUNPOD_SSH_KEY_B64 from the research tool's own key in `~/.local/state`.
- The store has no remote, so r20261001-104401-0d6a's 4 labels are local only.
- My `git push` of the notes fails. A notes sync started before the resume still has the token, and it pushes my local
  commits on its next pass, so notes arrive late rather than never.

I didn't copy secrets out of the older processes or recreate the files, since I couldn't tell whether they were removed on
purpose. Better: when an agent session resumes, it gets the same secrets the VM booted with, and `research` names any
missing one at startup instead of failing at the first push.
