---
id: red-team-proofs-554/20261002T0940Z-friction-masked-env-file-printed-key-lines
lane: red-team-proofs-554
kind: friction
status: open
severity: incident
recurs: note:circuits-grid-models/20261001T1517Z-friction-env-names-printed-key-lines
---

# A line-oriented mask over `~/.proofs-env/env.sh` printed lines of `NEBIUS_SA_PRIVATE_KEY`

At 09:37Z (2:37 AM PDT Oct 2) the notes push for #806's verdict failed because `RESEARCH_NOTES_TOKEN` wasn't set in my
shell.

- To find where it came from, I ran `sed -E 's/(=)[^ ]{12,}/\1<masked>/g' ~/.proofs-env/env.sh | head -40`.
- That mask works line by line. The PEM body of `NEBIUS_SA_PRIVATE_KEY` sits on lines with no `=`, so about 35 lines of
  the key went into this agent's tool output.
- Nothing reached the notes, git or the store.
- **Recommendation:** rotate that service-account key, as the earlier note also recommends.

**Use instead:** `rg -o '^export [A-Z_0-9]+' FILE` to list an env file's names, and `( . FILE >/dev/null 2>&1; cmd )` to
use the file without printing it.

**The better abstraction** is the same as the earlier note's: a `research env names` command that lists names safely,
for files as well as for the environment.
