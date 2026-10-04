---
id: circuits/20261004T2255Z-friction-notes-token-lost-in-new-shells
lane: circuits
kind: friction
status: open
recurs: note:proofs-bf16-hill/20261001T1138Z-friction-resumed-session-without-cursor-secrets
---

# New shells on a long-lived cloud VM stopped receiving RESEARCH_NOTES_TOKEN

On circuits' VM (`bc-b8aaadaa`, up 3.6 days), new shells have had an empty `RESEARCH_NOTES_TOKEN` since about 22:48Z,
4 Oct. A notes push at 22:43Z had worked. Processes started earlier still carry the token, and the secret is still set
on the owner's side. At the same time, worker `bc-e959c411`'s turn stopped on "repeated shell spawn failures", which
points to a shell-daemon restart that didn't pass the secrets on.

Cost: `research notes sync` failed with "Invalid username or token" until I noticed the token was missing (about 10
minutes). The local commit was kept.

Workaround: push with the token read from an older process's environment, which the owner approved. This keeps it in
the environment and out of argv and files. Run from the notes clone:
`RESEARCH_NOTES_TOKEN="$(tr '\0' '\n' </proc/<old pid>/environ | sed -n 's/^RESEARCH_NOTES_TOKEN=//p')" git push -q origin main`.

A fresh VM gets the token again. Better: `research notes sync` should say "RESEARCH_NOTES_TOKEN is empty in this shell"
before it pushes, instead of passing on git's authentication error.
