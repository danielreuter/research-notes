---
id: proofs/20261006T0900Z-friction-env-names-printed-key-line-again
campaign: proofs
lane: proofs
kind: friction
status: fixing
fix: "PR #1327 (infra): .cursor/hooks.json beforeShellExecution guard refuses env/printenv/set/export -p and /proc/*/environ; covers agents started after it lands"
severity: incident
recurs: note:circuits-grid-models/20261001T1517Z-friction-env-names-printed-key-lines
repo: verity
origin: [agent:bc-10800703-a761-59b5-bba7-ada86afaf5e7]
---

# Listing environment variable names printed a line of a multi-line private key again (firewall-contract, Oct 6 ~08:00Z)

A proofs worker (firewall-contract, on a fresh VM) listed the injected secrets' names and one line of a multi-line key, most
likely `NEBIUS_SA_PRIVATE_KEY`, went into its own transcript; nothing reached Slack, notes, git or the store. That is at least
the fifth time, even though `kb/cloud-lane-setup.md` says `compgen -e`, so a doc line isn't enough: the fix is a tool that
lists names safely (`research env names`) or a VM where the PEM isn't a multi-line env value. Rotation asked of Daniel
(card `4e298b1b`); proofs prompts now carry the `compgen -e` rule.

A second path, Oct 6 ~09:30Z: one-hash listed processes with full command lines on its own VM (checking memory), and a
local daemon's auth token was in one argv; it stayed in its tool output. #1327 doesn't cover `ps`. Proofs prompts now say:
never `ps aux`, `ps -ef`, `ps -eo args` or `pgrep -a`; use `ps -eo pid,stat,etimes,comm`. Told infra (1791279717.543699).
