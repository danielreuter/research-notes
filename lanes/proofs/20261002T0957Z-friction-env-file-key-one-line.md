---
id: proofs/20261002T0957Z-friction-env-file-key-one-line
campaign: e2e-guarantees
lane: proofs
kind: friction
status: open
severity: incident
recurs: note:red-team-proofs-554/20261002T0940Z-friction-masked-env-file-printed-key-lines
repo: verity
origin: proofs bc-8416bc72
---

# `NEBIUS_SA_PRIVATE_KEY` leaked twice through line-oriented commands; the env file now holds it on one line

The same multi-line PEM value leaked twice: through `env | cut` (`note:circuits-grid-models/20261001T1517Z-friction-env-names-printed-key-lines`)
and through a per-line `sed` mask over proofs' `~/.proofs-env/env.sh`. A worker started by proofs did the second, at 09:37Z.

- **Fixed at the source (proofs' VM, 2:55 AM PDT):** `env.sh` now holds the key as one base64 token right after an `=`,
  decoded on the next line. Sourcing it yields byte-identical values for all 18 variables (sha256 checked). The red team's
  own mask now leaves no key material.
- **Rule added** to proofs' worker brief (`internal/proofs/e2e/worker-common.md`): source the file, never print it, list
  names with `rg -o '^export [A-Z_0-9]+'` or `compgen -e`.
- **Still open, Daniel's:** rotate the Nebius service-account key. Both incidents put key lines into agent transcripts.
  Nothing reached git, the notes or the store.
- **Better abstraction (unchanged):** `research env names`. The process environment still carries a multi-line value, so
  `env | cut` stays unsafe until consumers take a single-line form.
