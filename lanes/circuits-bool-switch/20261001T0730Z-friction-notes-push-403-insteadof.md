---
id: 20261001T0730Z-friction-notes-push-403-insteadof
campaign: verity
lane: circuits-bool-switch
kind: friction
status: open
repo: danielreuter/verity
origin: circuits-bool-switch
---

# `research notes sync` failed with 403 for this lane: the VM's global `url.insteadOf` overrode the notes token

**What happened.** On this cloud VM, every `research notes sync` failed to push with "Permission to
danielreuter/research-notes.git denied to cursor[bot]". The commits stayed local, so nothing this lane wrote reached origin
until 12:30 AM PDT.

**The cause.** The global git config rewrites `https://github.com/` to a URL that carries the code repo's bot token
(`url.<…>.insteadOf`). That rewritten URL takes precedence over the notes clone's credential helper, which would have sent
`RESEARCH_NOTES_TOKEN`.

**The workaround.** I set the notes clone's remote URL to
`git remote set-url origin https://x-access-token@github.com/danielreuter/research-notes.git`. The `insteadOf` prefix doesn't
match that URL, so the helper's token is used, and pushes now succeed.

**The better fix.** `research notes sync` or the clone setup could set that URL itself. Or sync could print this cause when
the push returns 403.
