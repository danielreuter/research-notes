---
id: circuits-grid-models/20261001T1517Z-friction-env-names-printed-key-lines
lane: circuits-grid-models
kind: friction
status: open
severity: incident
---

# Listing environment variable names with `env | cut -d= -f1` printed lines of a multi-line private key

At 14:55Z, on a freshly restarted agent VM, I listed the injected secrets' names with `env | cut -d= -f1 | sort`.

- `NEBIUS_SA_PRIVATE_KEY` holds a multi-line PEM value. `cut` treats each of its lines as a variable, so lines of the key body went into this agent's tool output.
- Nothing reached the notes, git or the store.
- Recommendation: rotate that service-account key.
- What to use instead: `compgen -e` or `python3 -c 'import os; print(sorted(os.environ))'`, which print names only.
- The better abstraction: a `research env names` or a skill line that lists secret names safely, since every fresh cloud VM needs to check which secrets it has.
