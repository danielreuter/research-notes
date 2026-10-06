---
id: compute-accounting/20261006T0531Z-friction-audit-cwd-clone-warden-import
campaign: pouw
lane: compute-accounting
kind: friction
status: open
repo: danielreuter/verity
origin: rowseed-k lane (bc-49450b50), #1288
cursor:
  subagentId: "bc-e90634dd-8e87-5b7b-8ecd-97abfd87e3fa"
---

# `audit.py --build verity/Security` under `research run --cwd clone` fails at `Proofs`' Warden `runs` step

Run `r20261006-043928-0370` (vy-nebius-1, `audit.py --build verity/Security`, `--cwd clone`). `verity/Security` passed,
replay included. `verity/Security/Proofs` built and passed the replay, but its `runs` step failed:
`Proofs.Warden.DifftestMain`'s `generate` refused because `verity.protocols.accounting.communication.warden` resolved
from the run's shared source tree instead of the clone. So a full-replay audit of a PoUW Lean change can't reach an
overall PASS this way, and the lane spent a 45-minute run to find that out. `check`'s own lean-audit step is still the
verdict that counts.

Likely cause: the `runs` step's Python sees the run's source tree on `sys.path` (or an editable install of it) ahead of
the clone. That is the same class of fault as
`note:vllm-coverage-defs/20261001T0812Z-friction-source-identity-guard-fails-under-research-run`.

Until it's fixed: run the full audit with `--cwd source`, or let `check` do it.
