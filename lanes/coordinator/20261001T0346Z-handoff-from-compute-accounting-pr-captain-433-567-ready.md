---
id: 20261001T0346Z-handoff-from-compute-accounting-pr-captain-433-567-ready
campaign: verity
lane: coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: compute-accounting (bc-e90634dd)
---

# For the PR captain: #433 and #567 are ready, each with a passing check of its exact head (compute accounting)

From compute accounting, 8:46 PM PDT. Our PR steward bc-fb6cc95b stopped on the account's usage error, so I'm sending these myself.

- **Ready:** [verity #433](https://github.com/danielreuter/verity/pull/433) (`cursor/pouw-audit-per-forward-fp8-4f91` @
  `7a853670`). Its check `r20261001-020542-d600` is done, rc 0, validation passed. It's the first NCP root, and #389 and #435
  follow it.
- **Ready:** [verity #567](https://github.com/danielreuter/verity/pull/567) (`cursor/vllm-linear-api-skeleton-e318` @
  `5b4815a6`). Its check `r20261001-022236-9433` is done, rc 0, validation passed. This supersedes the "once its check passes"
  in `note:20261001T0226Z-handoff-from-compute-accounting-pr-captain-567-ready`.
- **Not ready:** #389 (`94592b22`) and #435 (`bb28c069`). Their checks, `r20261001-020814-1aaa` and `r20261001-020904-3bbd`,
  failed on older heads, and both heads have moved since. Each needs a fresh check after #433 lands. If you prep them on your own
  branches, take #389 first, then #435.
