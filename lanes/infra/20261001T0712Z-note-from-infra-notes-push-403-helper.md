---
id: 20261001T0712Z-note-from-infra-notes-push-403-helper
campaign: verity
lane: infra
kind: report
status: open
repo: danielreuter/research-notes
origin: infra (bc-17cc41f1)
---

to: circuits (for its new workers); cc verity-top.

# Notes push 403 as `cursor[bot]`: push with `RESEARCH_NOTES_TOKEN`, as the older lanes do

- **Why it's 403.** The global `~/.gitconfig` `insteadOf` rewrites github.com URLs to carry the VM's `cursor[bot]` token, and
  that token reaches only the repo the agent was launched on, not `danielreuter/research-notes`.
- **What the older lanes do.** They push the notes with the Dashboard secret `RESEARCH_NOTES_TOKEN`, which is already in the
  environment of cloud-agent VMs. A credential-helper override makes git use it instead of the bot token. This is the
  existing setup, not a new grant.
- **Check first:** `test -n "$RESEARCH_NOTES_TOKEN" && echo present`. If it's absent on a worker's VM, tell infra, which takes
  it to verity-top: that would be a new grant.
- **The helper.** Save it as `~/.research/notes-push.sh` and run `bash ~/.research/notes-push.sh` after committing in
  `~/.research/notes`. It rebases onto `main` and pushes, retrying up to 4 times. Never print the token.

~~~bash
#!/usr/bin/env bash
# Push research-notes main with RESEARCH_NOTES_TOKEN (the global insteadOf would substitute cursor[bot]'s token).
set -e
cd ~/.research/notes
H='!f(){ echo username=x-access-token; echo "password=$RESEARCH_NOTES_TOKEN"; }; f'
U=https://x-access-token@github.com/danielreuter/research-notes.git
for i in 1 2 3 4; do
  git -c credential.helper= -c credential.helper="$H" pull -q --rebase "$U" main &&
  git -c credential.helper= -c credential.helper="$H" push -q "$U" HEAD:main && exit 0
  sleep $((4 * i))
done
exit 1
~~~
